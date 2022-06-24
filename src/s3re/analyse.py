from pathlib import Path
import csv
import numpy as np
from numpy import fft
from scipy import signal
from scipy import stats
from matplotlib import pyplot as plt
import logging
from typing import Tuple, List, Callable
from s3re.detection import Detection
import matplotlib.patches as patches
import operator
import time
import multiprocessing
from joblib import Parallel, delayed

# Sampling rate. We set it to 1, in this way everything in our code is
# frequency-normalized.
fs = int(1)

# Analysis step in the time domain (in number of samples).
# This values is a trade-off: the larger it is, the better the resolution in the
# frequency domain but you lose resolution in the time domain, and vice-versa.
dt = int(2 ** 12)

# Threshold, expressed in dB, used to segment the signal in the time domain.
threshold_t = -20

# Threshold, expressed in dB, used to segment the spectrum in Bands-Of-Interest.
threshold_f = -30

# Threshold on 4th moment, used to split single-carrier from multi-carrier
# signals (and noise).
threshold_mc = 1e-2

# Size of FFTs used to display debug information.
nfft = int(2 ** 13)

# Global variable, used to assign a unique ID to the different detections.
detection_id = 0

# Enable/disable the list of detections used for graphical representation
# (warning! activating both this and debug information usually results in a
# messed-up list...)
print_detections = True

# Global list of rectangles to draw --- it's ugly, but it is here just for
# debugging purposes.
rectangles_to_draw = []

# Number of peaks to explore when seeking the symbol rate.
peaks_no = int(1e2)

# Limit on the length of the signal that is explored using the peak search
# algorithm. Both this number and the number of peaks to explore affect the
# computation time.
peak_exploration_sig_len = int(2 ** 16)

# Minimum length (in number of samples) of the detections that we are interested
# in. This limit will be enforced once detections have been adjusted.
min_samples_no = 2 * dt

# Number of I/Q shifts to attemps for estimating the symbol rate.
iq_shifts_no = 20

# Number of cores on which the peak inspection will take place.
num_cores = multiprocessing.cpu_count()

# Lower bound on the normalized frequency (will not explore symbol rates below
# this value --- saves computational resources and gets rid of low-frequency
# noise)
br_lower_bound = 1e-4

# Peak search region width
rw = 30


def freq_shift(x: np.ndarray, \
               df: float) -> np.ndarray:
    r"""Frequency-shift a given signal by the desired amount.

    Parameters
    ----------
    x: np.ndarray
    input signal
    df: float
    shift to impose (in (-.5, +.5))

    Returns
    -------
    y: np.ndarray
    frequency-shifted signal
    """
    xshift = np.array([np.exp(1j * df * 2 * np.pi * k) for k in range(0, len(x))])
    y = [x[i] * xshift[i] for i in range(0, len(x))]

    return np.asarray(y)


def extract_signal(x: np.ndarray, lf: float, hf: float,  debug: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    r"""Extract the signal comprised in the [lf, hf] frequency band.

    Parameters
    ----------
    x: np.ndarray
    array containing the signal to extract
    lf: float
    lowest frequency of the signal of interest
    hf: float
    highest frequency of the signal of interest
    debug: bool
    activate debug information/plots

    Returns
    -------
    z: np.ndarray
    extracted signal
    centered_x: np.ndarray
    filtered and centered signal
    h: np.ndarray
    filter used for the extraction
    lp_cfreq: float
    cut-off frequency
    """
    # Number of taps of the filter used to extract the signal of interest.
    # This number is pretty high, but so far it poses no issues on modern
    # microprocessors. If signals start to get big, it might be worth to
    # reduce it (at the price of having wider transition bands).
    ntaps = 283

    # Center the signal, so that we can low-pass filter it and have it
    # already in place.
    centered_x = freq_shift(x, -(lf + (hf - lf) / 2))

    # Cut-off frequency.
    lp_cfreq = (hf - lf) / 2

    # Filter. The sampling frequency is one epsilon above 1 because of a
    # silly limitation of Python (if the filter just has to take the whole
    # [-.5, .5] band, it wouldn't let it do so without this epsilon).
    h = signal.firwin(ntaps, lp_cfreq, pass_zero="lowpass", fs=1 + 1e-6)

    # Do the filtering via convolution.
    z = signal.convolve(centered_x, h, "same")

    # If we desire so, display debug information.
    if debug:
        plt.subplot(2, 1, 1)
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(x, nfft))))
        plt.axvline(lf, color="red")
        plt.axvline(lf + (hf - lf) / 2, color="red", ls="--")
        plt.axvline(hf, color="red")
        plt.title("Spectrum of input signal")

        plt.subplot(2, 1, 2)
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(centered_x, nfft))))
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(h, nfft))))
        plt.axvline(-lp_cfreq, color="red")
        plt.axvline(0, color="red", ls="--")
        plt.axvline(+lp_cfreq, color="red")
        plt.legend(["Centered signal", "Filter"])
        plt.title("Spectrum of centered signal")
        plt.show()

    return z, centered_x, h, lp_cfreq


def extract_signal_with_resampling(x: np.ndarray, lf: float, hf: float, debug: bool = False) -> np.ndarray:
    r"""Extract the signal comprised in the [lf, hf] frequency band,
    appropriately resampling it to match the new bandwidth.

    Parameters
    ----------
    x: np.ndarray
    array containing the signal to extract
    lf: float
    lowest frequency of the signal of interest
    hf: float
    highest frequency of the signal of interest
    debug: bool
    activate debug information/plots

    Returns
    -------
    y: np.ndarray
    extracted signal
    """
    z, centered_x, h, lp_cfreq = extract_signal(x, lf, hf, False)

    # Since the signal now occupies a much smaller bw, we can safely resample
    # it.
    resampling_factor = 1.0 / (hf - lf)

    y = signal.resample(z, int(np.ceil(len(z) / resampling_factor)))
    y[:] = [y[i] * resampling_factor for i in range(0, len(y))]

    # If we desire so, display debug information.
    if debug:
        plt.subplot(3, 1, 1)
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(x, nfft))))
        plt.axvline(lf, color="red")
        plt.axvline(lf + (hf - lf) / 2, color="red", ls="--")
        plt.axvline(hf, color="red")
        plt.title("Spectrum of input signal")
        plt.xlabel("Normalized frequency")
        plt.ylabel("V**2")

        plt.subplot(3, 1, 2)
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(centered_x, nfft))))
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(h, nfft))))
        plt.axvline(-lp_cfreq, color="red")
        plt.axvline(0, color="red", ls="--")
        plt.axvline(+lp_cfreq, color="red")
        plt.legend(["Centered signal", "Filter"])
        plt.title("Spectrum of centered signal")
        plt.xlabel("Normalized frequency")
        plt.ylabel("V**2")

        plt.subplot(3, 1, 3)
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(y, nfft))))
        plt.plot(np.linspace(-.5, .5, nfft),
                 np.abs(fft.fftshift(fft.fft(z, nfft))))
        plt.legend(["Resampled filtered signal", "Filtered signal"])
        plt.title("Spectrum of filtered and resampled signal")
        plt.xlabel("Normalized frequency")
        plt.ylabel("V**2")

        plt.show()

    return y


def freq_segmentation(x_chunks: np.ndarray, threshold_f: float, debug: bool = False) -> list:
    r"""Detect occupied bands in the power spectral density.

    Parameters
    ----------
    x_chunks: np.ndarray
    chunks of the input signal where energy has been detected
    threshold_f: float
    threshold to be imposed on bands-of-interest to detect the presence of a
    signal in the given band
    debug: bool
    activate debug information/plots

    Returns
    -------
    boi_per_chunk: list
    list of BOIs per each chunk. This list contains a sub-list for each
    chunk, and each sub-list contains pairs of start-end frequencies.
    """
    chunks_no, dt = x_chunks.shape
    boi_per_chunk = list()
    # Frequency step.
    df = 1 / dt
    # This parameter is used to de-glitch the spectrum detections. Basically,
    # all "holes" or "peaks" in the spectrum up to this width will be
    # ignored.
    deglitch_val = 100 * df
    for i in range(chunks_no):
        f, Pxx = signal.welch(x_chunks[i, :],
                              fs=1.0,
                              nfft=dt,
                              return_onesided=False,
                              scaling="spectrum")
        # Move frequency 0 in the middle.
        Pxx = fft.fftshift(Pxx)
        # Convert to logarithmic scale. This eases the setting of a
        # threshold (it would be quite tricky to get the threshold right
        # on a linear scale, especially to get all the sidelobes).
        np.where(Pxx < 1e-12, 1e-12, Pxx)
        # Keep a copy for comparison.
        linear_Pxx = Pxx.copy()
        Pxx = 10 * np.log10(Pxx)
        # Now adopt the same strategy used in the time domain.
        # At the beginning we are not in a signal.
        in_boi = False
        start_f_idx = 0
        N = len(Pxx)
        # List of BOIs for the current chunk.
        boi_chunk = list()
        for j in range(N):
            if not in_boi and Pxx[j] >= threshold_f:
                in_boi = True
                start_f_idx = j
            else:
                if in_boi and \
                        (Pxx[j] < threshold_f or j == N - 1):
                    # We also have to take into account the
                    # case where we get to the end of the
                    # spectrum and we are still marked as
                    # "in a BOI".
                    # Filter out glitches.
                    in_boi = False
                    if (j - start_f_idx) * df > deglitch_val:
                        boi_chunk.append([start_f_idx * df - .5,
                                          j * df - .5])
        # Process the list for the current chunk. If two adjacent BOIs
        # are separated by less than a glitch, merge them.
        merged_boi = list()
        j = 1
        if len(boi_chunk) == 1:
            # Only one detection, we can safely push it as boi.
            merged_boi.append(boi_chunk[0])
        else:
            if len(boi_chunk) > 1:
                current_boi = boi_chunk[0]
            while j < len(boi_chunk):
                if boi_chunk[j][0] - current_boi[1] <= deglitch_val:
                    current_boi = [current_boi[0], boi_chunk[j][1]]
                else:
                    merged_boi.append(current_boi)
                    current_boi = boi_chunk[j]
                if j == len(boi_chunk) - 1:
                    merged_boi.append(current_boi)
                j += 1

        if debug:
            plt.subplot(2, 1, 1)
            plt.plot(np.linspace(-.5, .5, N), Pxx)
            for j in range(len(merged_boi)):
                plt.axvline(merged_boi[j][0], color="red")
                plt.axvline(merged_boi[j][1], color="red")
            plt.title("Power spectrum on a logarithmic scale")
            plt.xlabel("Normalized frequency")
            plt.ylabel("Power [dB]")
            plt.subplot(2, 1, 2)
            plt.plot(np.linspace(-.5, .5, N), linear_Pxx)
            for j in range(len(merged_boi)):
                plt.axvline(merged_boi[j][0], color="red")
                plt.axvline(merged_boi[j][1], color="red")
            plt.title("Power spectrum on a linear scale")
            plt.xlabel("Normalized frequency")
            plt.ylabel("Power [V**2]")
            plt.show()

        boi_per_chunk.append(merged_boi)

    return boi_per_chunk


def add_value_in_dict(detections_dict: dict, pos: int, new_detection_idx: int) -> dict:
    r"""Append a value to a key in the given dictionary. In particular, this
    dictionary will be used to store the list of bands to update given a new
    detection in the subsequent signal chunk.

    @TODO: for the moment, if a previous value is detected, it is discarded.
    This is a crude approximation that should be fixed!

    Parameters
    ----------
    detections_dict: dict
    dictionary that pairs up detections to update with their detections in
    the current signal chunk
    pos: int
    position in the dictionary of the detection to update
    new_detection_idx: int
    newly, updated position

    Returns
    -------
    detections_dict: dict
    Updated dictionary.
    """
    if pos not in detections_dict:
        detections_dict[pos] = list()
        detections_dict[pos].append(new_detection_idx)
    else:
        detections_dict[pos][0] = new_detection_idx

    return detections_dict


def boi_is_present(boi: list, occupied_bands: List[Detection], tol: float) -> Tuple[bool, int]:
    r"""Check whether a given Band Of Interested (detected signal in the
    frequency domain) is already present in the list of occupied bands
    (taking a tolerance into account)

    Parameters
    ----------
    boi: list
    detected Band Of Interest
    occupied_bands: list
    list of already occupied bands
    tol: float
    tolerance that has to be taken into account in the comparisons

    Returns
    -------
    If the BOI is already present, True and the BOI's index. Otherwise, False
    and -1 to signal that the BOI is not yet known to the system.
    """
    for i in range(len(occupied_bands)):
        if occupied_bands[i].get_last_lfreq() - tol < boi[0] and \
                occupied_bands[i].get_last_hfreq() + tol > boi[1]:
            return True, i
    return False, -1


def analyze_chunks(x_chunks: np.ndarray, \
                   start_sample: int, \
                   end_sample: int, \
                   threshold_f: float, \
                   user_cb: Callable[[np.ndarray, int, Detection], None], \
                   debug: bool = False) -> None:
    r"""Take the time chunks marked as occupied by a signal and explore their
    spectral occupancy.

    Parameters
    ----------
    x_chunks: np.ndarray
    signal chunks marked by the time segmentation algorithm as occupied by a
    signal
    start_sample: int
    index of the starting sample of the chunk block
    end_sample: int
    index of the last sample of the chunk block
    threshold_f: float
    threshold used to segment the spectrum in bands
    user_cb: Callable[[np.ndarray, int, Detection], None]
    user-specified callback function, invoked on each detection (a
    "rectangle" in the spectrogram)
    debug: bool
    activate debug information/plots
    """
    chunks_no, dt = x_chunks.shape
    # Frequency step.
    df = 1 / dt
    global detection_id
    if debug:
        logging.debug("Analyzing chunks from " +
                      str(start_sample) +
                      " to " +
                      str(end_sample) +
                      ", chunks_no = " +
                      str(chunks_no) +
                      ", dt = " +
                      str(dt))
    # Retrieve the list of bands in each chunk.
    boi_per_chunk = freq_segmentation(x_chunks,
                                      threshold_f,
                                      debug)
    # Now process the list of BOIs for each chunk, merging the adjacent ones
    # and setting the different detections.
    occupied_bands = list()
    detections = list()
    for i in range(chunks_no):
        boi = boi_per_chunk[i]
        if debug:
            logging.debug("\n\nBOIs at iteration " + str(i) + " :\n" + str(boi))
            logging.debug("--------- Currently occupied bands ---------")
            for j in range(len(occupied_bands)):
                logging.debug(str(occupied_bands[j].id) +
                              ": " +
                              str(occupied_bands[j].get_last_lfreq()) +
                              " -> " +
                              str(occupied_bands[j].get_last_hfreq()))
            logging.debug("--------------------------------------------")

        # We now check whether a new band has been occupied, or a
        # previously occupied one has been freed.
        to_update = dict()
        new_bands = list()
        for b in range(len(boi)):
            if debug:
                logging.debug("Checking " + str(boi[b]))
            is_present, pos = boi_is_present(boi[b],
                                             occupied_bands,
                                             100 * df)
            # We try to avoid spurious detections close to the end of
            # the time detection.
            if not is_present and i < chunks_no:
                new_bands.append(Detection(detection_id,
                                           start_sample + i * dt,
                                           boi[b][0], boi[b][1]))
                detection_id += 1
                if debug:
                    logging.debug("Boi not present, appending it to the new ones")
                    logging.debug("------- Current state of the new boi list -----")
                    for j in range(len(new_bands)):
                        logging.debug(str(new_bands[j].id) +
                                      ": " +
                                      str(new_bands[j].get_last_lfreq())
                                      + " -> " +
                                      str(new_bands[j].get_last_hfreq()))
                    logging.debug("-----------------------------------------------")
            else:
                # Watch out! If two signals cross (e.g., two
                # chirps in opposite frequency "directions"),
                # there could be more than one pair with 'pos'
                # as second index!
                add_value_in_dict(to_update, pos, b)
                if debug:
                    logging.debug("BOI present, current to_update: " + str(to_update))
        if debug:
            logging.debug("----- NEW DETECTIONS -----")
            for j in range(len(new_bands)):
                logging.debug(new_bands[j])
            logging.debug("--------------------------")
        confirmed = new_bands
        # Check those that have been confirmed
        for old_boi, new_boi in to_update.items():
            for j in range(len(new_boi)):
                confirmed.append(occupied_bands[old_boi])
        # Keep only the new ones, all the others are discarded.
        freed_boi = np.setdiff1d(list(range(len(occupied_bands))), list(to_update.keys()))
        if debug:
            logging.debug("range(len(occupied_bands)): " + str(list(range(len(occupied_bands)))))
            logging.debug("keys(): " + str(list(to_update.keys())))
            logging.debug("List of freed: " + str(freed_boi) + ", marking them as completed!")
        for j in range(len(freed_boi)):
            if debug:
                logging.debug("Adding: " + str(occupied_bands[freed_boi[j]]))
            # These BOI ended, we can thus add them to the list.
            occupied_bands[freed_boi[j]].set_end(start_sample + i * dt - 1, x_chunks)
            detections.append(occupied_bands[freed_boi[j]])
        occupied_bands = confirmed

    # All the BOI left here end because the time segment ends. We add them to
    # the detection list.
    for j in range(len(occupied_bands)):
        if debug:
            logging.debug("Adding (left at end): " + str(occupied_bands[j]))
        occupied_bands[j].set_end(end_sample - 1, x_chunks)
        detections.append(occupied_bands[j])

    # Now go over detections and assing to each of them a unique upper and
    # lower frequency (taking the mean of what they have seen over time).
    for j in range(len(detections)):
        detections[j].average_frequencies()

    # When we get to here, all the detections for the current time chunk are
    # done. However, it could happen that a detection gets merged with a
    # neighboring one that suddenly appeared (or that two detections that
    # were merged by mistake reveal themselves to be two distinct
    # transmissions, once one of them quits).
    # Here we thus look for these situations and split/merge detections when
    # appropriate.
    for j in range(len(detections)):
        # Look for neighbors in time and adjust them if needed.
        for k in range(j + 1, len(detections)):
            if abs(detections[k].start_sample - detections[j].end_sample) < 100 and \
                    (np.abs(detections[j].l_freq - detections[k].l_freq) < 100 * df or \
                     np.abs(detections[j].h_freq - detections[k].h_freq) < 100 * df):
                detections[j], detections[k] = adjust_detections(x_chunks,
                                                                 start_sample,
                                                                 detections[j],
                                                                 detections[k],
                                                                 df,
                                                                 dt,
                                                                 threshold_f,
                                                                 debug)

    # Drop detections that are too small (in number of samples).
    to_keep = list()
    for j in range(len(detections)):
        if detections[j].end_sample - detections[j].start_sample >= min_samples_no:
            to_keep.append(detections[j])
    detections = to_keep.copy()

    # Output detections in a format suitable for the rectangles to plot.
    if print_detections:
        for j in range(len(detections)):
            global rectangles_to_draw
            if detections[j].h_freq > 0.49:
                detections[j].h_freq = 0.49
            rectangles_to_draw.append([detections[j].start_sample,
                                       detections[j].l_freq,
                                       detections[j].end_sample,
                                       detections[j].h_freq])

    # We can now call the callback function given by the user, which will in
    # turn perform some analysis on the different detections.
    for j in range(len(detections)):
        user_cb(x_chunks, start_sample, detections[j])


def time_segmentation(x: np.ndarray, \
                      dt: int, \
                      threshold_t: float, \
                      threshold_f: float, \
                      user_cb: Callable[[np.ndarray, int, Detection], None], \
                      debug: bool = False) -> None:
    r"""Detect the signal in the time domain using a threshold on signal
    power. This threshold is expressed in dB. As such, it *strictly depends*
    on the chosen bandwidth: if one considers a wider bandwidth, the noise
    spreads out. For instance, if we take twice the bandwidth, the noise in
    each bin decreases by 3 dB... This means that a threshold that happily
    separates the signal from the noise could reveal itself totally useless
    when the FFT size (here given by 'dt', that is, the chunk size) is too
    small.
    To avoid fragmenting the signal too much due to noise (e.g., the
    amplitude of an ASK signal keeps varying over time, and the speed of
    these changes is given by the (unknown) symbol rate), the signal is split
    in chunks with size 'dt'. These chunks also contribute to the detection
    of signal bursts -- a silent chunk is big enough to mark the step between
    two bursts.
    When a set of time-domain chunks is marked as containing one (or more)
    signals, an analysis is performed in the frequency domain.

    Parameters
    ----------
    x: np.ndarray
    input signal
    dt: int
    size (in number of samples) of the time-domain chunks
    threshold_t: float
    threshold (in dB) used to distinguish signal chunks from noise ones in
    the time domain
    threshold_f: float
    threshold (in dB) used to distinguish signal bands from noise ones in the
    frequency domain
    user_cb: Callable[[np.ndarray, int, Detection], None]
    user-provided callback function, passed to the frequency segmentation
    function
    debug: bool
    activate debug information/plots
    """
    # Split the signal in chunks of equal size (given by dt). We drop some
    # samples at the end if the last chunk is incomplete.
    chunks_no = int(np.floor(len(x) / dt))
    x = x[0:dt * chunks_no]
    split_x = np.reshape(x, (chunks_no, dt))

    # At the beginning we are not in a signal
    in_sig = False
    start_idx = 0
    # Go over the chunks one at a time and check their mean power level.
    # Since we are operating in dB, to avoid having numerical issues, zeros
    # in the power spectrum are replaced by an epsilon.
    for i in range(0, chunks_no):
        f, Pxx = signal.welch(split_x[i, :],
                              fs=1.0,
                              nfft=dt,
                              return_onesided=False,
                              scaling="spectrum")
        # Move frequency 0 in the middle.
        Pxx = fft.fftshift(Pxx)
        # Convert to logarithmic scale. This eases the setting of a
        # threshold (it would be quite tricky to get the threshold right
        # on a linear scale, especially to get all the sidelobes).
        np.where(Pxx < 1e-12, 1e-12, Pxx)
        Pxx = 10 * np.log10(Pxx)
        if debug:
            plt.plot(np.linspace(-.5, .5, dt), Pxx)
            plt.title("Power spectrum for chunk " + str(i))
            plt.show()
        # Now get the max power for the chunk and use it to detect
        # chunks containing signals.
        max_pwr = np.max(Pxx)

        if not in_sig and max_pwr >= threshold_t:
            in_sig = True
            start_idx = i
        else:
            if in_sig and \
                    (max_pwr < threshold_t or i == chunks_no - 1) and \
                    start_idx < i:
                # We also have to take into account the case
                # where we get to the end of the signal and we
                # are still marked as "in the signal".
                in_sig = False
                analyze_chunks(split_x[start_idx:i + 1, :],
                               start_idx * dt,
                               (i + 1) * dt - 1,
                               threshold_f,
                               user_cb,
                               debug)


def adjust_detections(x_chunks: np.ndarray, \
					  chunks_start: int, \
					  d1: Detection, \
					  d2: Detection, \
					  df: float, \
					  dt: int, \
					  threshold_f: float, \
					  debug: bool) -> Tuple[Detection, Detection]:
		r"""Fix the issue with neighboring detections getting glued together. In
		particular, this function avoids that a signal in a neighboring band
		results in two separate detection in the time domain, with one of the
		two encompassing both signals in the frequency domain.

		Parameters
		----------
		x_chunk: np.ndarray
		input signal chunks
		chunks_start: int
		sample number corresponding to the initial chunk (used to refer sample
		numbers to the overall signal, and not have them relative to the specific
		chunks we are working on
		d1: Detection
		first detection of the pair to adjust
		d2: Detection
		second detection of the pair to adjust
		df: float
		frequency resolution
		dt: int
		size of each chunk in time
		threshold_f: float
		detection threshold in the frequency domain
		debug: bool
		activate debug information/plots

		Returns
		-------
		Updated detections.
		"""
		# Delta used to detect a difference in the logarithmic plot that marks
		# the end of a signal
		sig_end_delta = 10

		# Set start and end samples relative to the chunks start.
		d1_start = int((d1.start_sample - chunks_start) / dt)
		d1_end = int((d1.end_sample+1 - chunks_start) / dt)
		d2_start = int((d2.start_sample - chunks_start) / dt)
		d2_end = int((d2.end_sample+1 - chunks_start) / dt)

		# The only difference in the algorithm are the frequency bands for the
		# two detections, we thus adapt them and apply the same algorithm in all
		# cases.
		if np.abs(d1.l_freq - d2.l_freq) < 100*df:
				if d1.h_freq > d2.h_freq:
						# *******|
						# *******|****
						d1.l_freq = d2.h_freq
						d1.h_freq = d1.h_freq
						d2.l_freq = d2.l_freq
						d2.h_freq = d2.h_freq
				else:
						#     |*******
						# ****|*******
						d1.l_freq = d1.l_freq
						d1.h_freq = d1.h_freq
						d2.l_freq = d1.h_freq
						d2.h_freq = d2.h_freq
		else:
				if d1.l_freq > d2.l_freq:
						# ****|*******
						#     |*******
						d1.l_freq = d1.l_freq
						d1.h_freq = d1.h_freq
						d2.l_freq = d2.l_freq
						d2.h_freq = d1.l_freq
				else:
						# *******|****
						# *******|
						d1.l_freq = d1.l_freq
						d1.h_freq = d2.l_freq
						d2.l_freq = d2.l_freq
						d2.h_freq = d2.h_freq
		# Upper/lower index for each detection (in the frequency domain).
		d1_f_idx_l = int((d1.l_freq+.5) / df)
		d1_f_idx_h = int((d1.h_freq+.5) / df)
		d2_f_idx_l = int((d2.l_freq+.5) / df)
		d2_f_idx_h = int((d2.h_freq+.5) / df)

		# Seek d2 start.
		j = d1_start
		found = False
		while j < d2_end and found == False:
				f, Pxx = signal.welch(x_chunks[j, :],
									  fs=1.0,
									  nfft=dt,
									  return_onesided=False,
									  scaling="spectrum")
				# Move frequency 0 in the middle.
				Pxx = fft.fftshift(Pxx)
				np.where(Pxx < 1e-12, 1e-12, Pxx)
				Pxx = 10*np.log10(Pxx)
				if np.mean(Pxx[d2_f_idx_l:d2_f_idx_h]) > threshold_f:
						found = True
						d2.start_sample = chunks_start + j*dt
						d2_start = j
				j += 1

		# Seek d1 start.
		j = d1_start
		found = False
		while j < d2_end and found == False:
				f, Pxx = signal.welch(x_chunks[j, :],
									  fs=1.0,
									  nfft=dt,
									  return_onesided=False,
									  scaling="spectrum")
				# Move frequency 0 in the middle.
				Pxx = fft.fftshift(Pxx)
				np.where(Pxx < 1e-12, 1e-12, Pxx)
				Pxx = 10*np.log10(Pxx)
				if np.mean(Pxx[d1_f_idx_l:d1_f_idx_h]) > threshold_f:
						found = True
						d1.start_sample = chunks_start + j*dt
						d1_start = j
				j += 1

		# Seek d2 end.
		j = d2_start+1
		found = False
		while j < d2_end and found == False:
				f, Pxx = signal.welch(x_chunks[j, :],
									  fs=1.0,
									  nfft=dt,
									  return_onesided=False,
									  scaling="spectrum")
				# Move frequency 0 in the middle.
				Pxx = fft.fftshift(Pxx)
				np.where(Pxx < 1e-12, 1e-12, Pxx)
				Pxx = 10*np.log10(Pxx)
				if np.mean(Pxx[d2_f_idx_l:d2_f_idx_h]) < threshold_f+sig_end_delta:
						found = True
						d2.end_sample = chunks_start + j*dt - 1
				j += 1

		# Seek d1 end.
		j = d1_start+1
		found = False
		while j < d2_end and found == False:
				f, Pxx = signal.welch(x_chunks[j, :],
									  fs=1.0,
									  nfft=dt,
									  return_onesided=False,
									  scaling="spectrum")
				# Move frequency 0 in the middle.
				Pxx = fft.fftshift(Pxx)
				np.where(Pxx < 1e-12, 1e-12, Pxx)
				Pxx = 10*np.log10(Pxx)
				if np.mean(Pxx[d1_f_idx_l:d1_f_idx_h]) < threshold_f+sig_end_delta:
						found = True
						d1.end_sample = chunks_start + j*dt
				j += 1

		# We have updated the two detections, we can thus return them.
		return d1, d2


def is_multicarrier(x: np.ndarray, debug: bool = False) -> bool:
		r"""Determine whether a given signal is a multi-carrier signal (FBMC,
		OFDM, ...) or not.

		Parameters
		----------
		x: np.ndarray
		input signal
		debug: bool
		activate debug information/plots

		Returns
		-------
		True if the signal is multi-carrier, False if it is single-carrier
		"""
		# Compute the 4th moment of both the real and the imaginary parts. If any
		# of the two, normalized on the length of the signal, is greater than
		# 1e3, then the signal is *not* multi-carrier (multi-carrier signals tend
		# to be Gaussian distributed, due to the Central Limit Theorem.
		rsnt = stats.kstat(np.real(x), n=4) / len(x)
		isnt = stats.kstat(np.imag(x), n=4) / len(x)
		global threshold_mc

		if debug:
				logging.debug("Signal length = " + str(len(x)))
				logging.debug("MC test -- rsnt: " + str(rsnt) +
							 ", isnt: " + str(isnt) +
							 " (threshold is " + str(threshold_mc) + ")")

		if np.abs(rsnt) > threshold_mc or np.abs(isnt) > threshold_mc:
				# if debug:
				# 		logging.debug("Signal is most likely SINGLE-CARRIER")
				return False
		else:
				# if debug:
				# 		logging.debug("Signal is most likely MULTI-CARRIER (or NOISE)")
				return True


def is_noise(x: np.ndarray, debug: bool = False) -> bool:
		r"""Check if a given signal is composed only by uncorrelated samples
		(thus, most likely, noise).

		Parameters
		----------
		x: np.ndarray
		input signal
		debug: bool
		activate debug information/plots

		Returns
		-------
		True if the signal is likely to be noise, False otherwise
		"""
		# We could simply check the autocorrelation for significant spikes other
		# than the one at zero. However, this would fail for alpha-stable noise,
		# since it would have many spikes around that would confuse our
		# algorithm. We instead chose to first drop the values that, in absolute
		# value, are in the highest X% (with X == 5). This should drop all the
		# unwanted spikes and give back an almost flat floor in the case where
		# no signal is present.
		# This approach is suggested here:
		# https://cyclostationary.blog/2019/08/22/on-impulsive-noise-csp-and-correntropy/
		idx_sort = np.argsort(x)
		N = len(x)
		X = 0.1
		# Radius of samples used in the interpolation process (that is, up to
		# this amount of samples on both sides of the desired sample will be
		# used in the interpolation).
		rad = 20
		# From this index on-wards, interpolate away the samples that are in the
		# top X%.
		start_idx = int(np.floor(N * (1 - X)))
		for i in range(start_idx, N):
				start_idx = max(1, idx_sort[i]-rad)
				end_idx = min(N, idx_sort[i]+rad)
				idxs = np.concatenate([np.arange(start_idx, idx_sort[i]),
									   np.arange(idx_sort[i]+1, end_idx)])
				x[idx_sort[i]] = np.interp(idx_sort[i], idxs, x[idxs])

		w = signal.correlate(x, x, mode="same")
		peaks, _ = signal.find_peaks(np.abs(w))
		peak_vals = np.abs(w[peaks])

		N = 5
		thr = 20
		# Get the index of the N largest peaks, then compare the values with the
		# largest one (by definition, it is the peak at zero displacement, since
		# it is an autocorrelation).
		idxs_max = peak_vals.argsort()[-N:][::-1]

		if debug:
				logging.debug("Noise check: " +
							 str(np.mean(peak_vals[idxs_max[1:N]])) +
							 ", threshold is " +
							 str(peak_vals[idxs_max[0]]/thr))

		if np.mean(peak_vals[idxs_max[1:N]]) > peak_vals[idxs_max[0]]/thr:
				return False
		return True


def nc_scohf_via_fsm(x: np.ndarray, alphas: list) -> list:
		r"""Compute the average Spectral Coherence Function value for a given
		list of cyclic frequencies using the Frequency Smoothing Method (FSM).

		Parameters
		----------
		x: np.ndarray
        input signal
		alphas: list
        cyclic frequencies of interest

		Returns
		-------
		S: list
        average SCohF value for the requested cyclic frequencies

		Warnings
		--------
		Compared to the "official" SCohF, we do not do the zero padding (since,
		empirically, it worsened the performances)

		See Also
		--------
		https://cyclostationary.blog/2016/01/08/the-spectral-coherence-function/
		"""
		# X(f).
		Xp = fft.fft(x)
		N = len(x)

		# Number of cyclic frequencies for which the SCohF has to be computed.
		Ncf = len(alphas)

		# The resulting SCohF values will be stored in this list.
		S = []

		# Smoothing filter. It must have a length of approximately 0.1-0.5% of
		# the signal length.
		fLen = int(np.ceil(N * 0.005))
		G = 1 / fLen * np.ones(fLen)

		# Iterate over the desired candidate cyclic frequencies and perform the
		# computation.
		for aIdx in range(0, Ncf):
				alpha = alphas[aIdx]

				# We have to find the values that best match the given alpha / 2
				# value (given FFTs resolution). Each sample shift will be 1 / N
				# (normalized Hz), therefore we will have to find m such that
				# m / N is close to alpha / 2.
				shiftVal = int(np.round((alpha / 2) * N))

				# Compute the cyclic periodogram.
				cp = 1 / N * np.roll(Xp, +shiftVal) * np.conj(np.roll(Xp, -shiftVal))
				cp_smooth = np.convolve(fft.fftshift(cp), G, mode="same")

				# Compute the normalization factors required to get the coherence
				# function.
				n_plus = 1 / N * np.roll(Xp, +shiftVal) * np.conj(np.roll(Xp, +shiftVal))
				n_plus_smooth = np.convolve(fft.fftshift(n_plus), G, mode="same")
				n_minus = 1 / N * np.roll(Xp, -shiftVal) * np.conj(np.roll(Xp, -shiftVal))
				n_minus_smooth = np.convolve(fft.fftshift(n_minus), G, mode="same")

				# Compute the SCohF value and append it to the list that will be
				# returned. To avoid division-by-zero (though, in principle, only
				# possible in simulated settings), we set the coherence to zero
				# whenever one of the two elements at the denominator is zero.
				if any(n_plus_smooth == 0) or any(n_minus_smooth == 0):
						S.append(0)
				else:
						S.append(np.mean(np.abs(cp_smooth / np.sqrt((n_plus_smooth * n_minus_smooth)))))

		return S


def inspect_peaks(x_nl_freq: np.ndarray, sig: np.ndarray, debug: bool = False) -> Tuple[float, float]:
		r"""Compute the index (in the FFT representation, thus in a normalized
		frequency vector) of the most prominent peak (or, possibly, a peak one
		octave lower) of a given signal.

		Parameters
		----------
		x_nl_freq: np.ndarray
		spectrum of a non-linearized version of the input signal
		sig: np.ndarray
		input signal
		debug: bool
		activate debug information/plots

		Returns
		-------
		sr_peak_freq: float
		estimated symbol rate frequency (in normalized frequency units, that is,
		in (0, 0.5))
		peak_value: float
		value at the detected symbol rate frequency
		"""
		# Take only a slice of the signal (the central one, to avoid weird
		# effects on signal's borders) to limit computation time.
		N = len(sig)
		M = min(N, peak_exploration_sig_len)
		start_idx = int(np.floor((N-M) / 2))
		sig = sig[start_idx : start_idx+M]

		nfft = len(x_nl_freq)
		# Seek peaks only in the positive frequency range.
		peaks, _ = signal.find_peaks(x_nl_freq[:int(nfft/2)])
		# Peak values.
		peak_vals = x_nl_freq[peaks]
		# Peak frequencies (normalized).
		peaks_freqs = np.array([peaks[i] / nfft for i in range(len(peaks))])

		# Discard peaks with a (normalized) frequency below a user-selected
		# lower bound
		idx_ok = np.array([S for S in range(len(peaks_freqs)) if peaks_freqs[S] > br_lower_bound])
		peak_vals = peak_vals[idx_ok]
		peaks_freqs = peaks_freqs[idx_ok]

		# Get the index of the N largest peaks, with the indexes of the largest
		# ones first. Then sort back (since we are just interested in picking the
		# largest N peaks, and not having them already sorted by value --- which
		# would make subsequent processing difficult).
		idx_max = np.sort(peak_vals.argsort()[-peaks_no:][::-1])

		if debug:
				plt.plot(np.linspace(0, 0.5, int(np.floor(nfft/2))),
						 x_nl_freq[0:int(np.floor(nfft/2))])
				plt.plot(np.array(peaks_freqs)[idx_max.astype(int)],
						 np.array(peak_vals)[idx_max.astype(int)], "x")
				plt.title("Peaks identified in the FFT magnitude")
				plt.xlabel("normalized frequency")
				plt.ylabel("|FFT(x)|")
				plt.show()

		# Get a sufficient number of peaks, then compute the SCF for each of them
		# -> the largest peak (discarding its harmonics) will be the symbol rate.
		alphas = np.array(peaks_freqs)[idx_max.astype(int)]

		S = nc_scohf_via_fsm(sig, alphas)

		# Remove from each value the local median value, just to make
		# true peaks stand out.
		avg_radius = 3
		S_avg = np.zeros(len(S))
		for j in range(peaks_no):
				start_idx =  max(0, j-avg_radius)
				if start_idx + 2*avg_radius >= peaks_no:
						start_idx = peaks_no-2*avg_radius
				end_idx = min(start_idx + 2*avg_radius+1, peaks_no)
				local_mean = 0
				cnt = 0
				if j > start_idx:
						local_mean += np.mean(S[start_idx:j])
						cnt += 1
				if end_idx > j+1:
						local_mean += np.mean(S[j+1:end_idx])
						cnt += 1
				if cnt > 0:
						local_mean /= cnt
				S_avg[j] = S[j] - local_mean

		if debug:
				plt.subplot(3, 1, 1)
				plt.plot(alphas, S)
				plt.title("SCohF")
				plt.xlabel("normalized frequency")
				plt.ylabel("|SCohF(x)|")
				plt.subplot(3, 1, 2)
				plt.plot(alphas, S_avg)
				plt.title("SCohF after the local average has been removed")
				plt.xlabel("normalized frequency")
				plt.ylabel("|SCohF(x)| - localAvg(|SCohF(x)|)")
				plt.subplot(3, 1, 3)
				plt.plot(alphas[1:], np.diff(S_avg))
				plt.title("diff of the SCohF")
				plt.show()

		# Sort SCohF values and consider only the largest two.
		sort_index = np.argsort(S_avg)

		# Index corresponding to the currently detected frequency.
		idx_freq = int(alphas[sort_index[-1]]*nfft)

		# Consider the region around the currently detected frequency
		# as well as the first three sub-harmonics. To avoid giving too
		# importance to the current frequency, its maximum value is
		# divided by 2.
		a = np.max(x_nl_freq[np.array(range(max(idx_freq-rw, 0), min(idx_freq+rw, len(x_nl_freq))))])/2
		b = np.max(x_nl_freq[np.array(range(max(idx_freq//2-rw, 0), min(idx_freq//2+rw, len(x_nl_freq))))])
		c = np.max(x_nl_freq[np.array(range(max(idx_freq//3-rw, 0), min(idx_freq//3+rw, len(x_nl_freq))))])
		d = np.max(x_nl_freq[np.array(range(max(idx_freq//4-rw, 0), min(idx_freq//4+rw, len(x_nl_freq))))])
		if debug:
				print("Sub-harmonics and corresponding NL-signal values:")
				print(str(idx_freq/nfft) + " -> " + str(a))
				print(str(idx_freq/(2*nfft)) + " -> " + str(b))
				print(str(idx_freq/(3*nfft)) + " -> " + str(c))
				print(str(idx_freq/(4*nfft)) + " -> " + str(d))
				print("---------------------------------")

		# Corresponding values in the non-linearized version of the
		# signal.
		vals = np.array([a, b, c, d])
		# Corresponding frequencies.
		idxf = np.array([idx_freq/nfft, idx_freq/(2*nfft), idx_freq/(3*nfft), idx_freq/(4*nfft)])
		# Sort by value, then take the highest.
		idxSS = vals.argsort()

		return idxf[idxSS[-1]], vals[idxSS[-1]]


def signal_nl_transform_freq(x: np.ndarray, debug: bool) -> np.ndarray:
		r"""Non-linearly transform an input signal to expose the candidate
		symbol rates.

		Parameters
		----------
		x: np.ndarray
		input signal
		debug: bool
		activate debug information/plots

		Returns
		-------
		xad_abs_f: np.ndarray
		input signal, in the frequency domain, after non-linear transformations
		"""
		# Non-linearities applied to the signal to signal to expose the candidate
		# symbol rates.
		x_angle = np.arctan(x)
		x_angle_diff = np.diff(x_angle)
		# FFT size. Take the maximum one we can afford given the samples we have.
		nfft = len(x_angle_diff)
		xad_abs_f = np.abs(fft.fft(np.abs(x_angle_diff), nfft))

		if debug:
				plt.subplot(3, 1, 1)
				plt.plot(np.abs(x_angle))
				plt.title("arctan(signal)")
				plt.xlabel("sample number")
				plt.ylabel("|arctan(x)|")
				plt.subplot(3, 1, 2)
				plt.plot(np.abs(x_angle_diff))
				plt.title("diff(arctan(signal))")
				plt.xlabel("sample number")
				plt.ylabel("diff(|arctan(x)|)")
				plt.subplot(3, 1, 3)
				plt.plot(np.linspace(-.5, .5, nfft), np.abs(fft.fftshift(xad_abs_f[0:nfft])))
				plt.title("FFT transform of the absolute value of the above")
				plt.xlabel("normalized frequency")
				plt.ylabel("|FFT(x)|")
				plt.show()

		return xad_abs_f


def inspect_single_shift(w: int, sig: np.ndarray, debug: bool = False) -> Tuple[float, float]:
		r"""Inspect a single sample shift (given by the 'w' parameter), analysing
		the peaks that emerge.

		Parameters
		----------
		w: int
		shift to apply, in number of samples
		sig: np.ndarray
		input signal
		debug: bool
		activate debug information/plots

		Returns
		-------
		sr: float
		estimated symbol rate (in normalized frequencies)
		pval: float
		peak value
		"""
		if w > 0:
				y_r = np.real(sig)
				y_j = np.imag(sig)
				y = y_r[0:-w] + 1j * y_j[w:]
		else:
				# The first iteration gets no shift.
				y = sig
		# Take the NL transform of the signal and inspect the peaks in
		# what is returned.
		x_nl_freq = signal_nl_transform_freq(y, debug)
		pfreq, pval = inspect_peaks(x_nl_freq, y, debug)
		sr = round(pfreq, 4)

		return sr, pval


def estimate_sr(sig: np.ndarray, samp_rate : float,  debug: bool = False) -> float:
		r"""Estimate the symbol rate of the input signal using a non-linearity
		and CSP. In particular, it looks for the location of the peaks in the
		spectrum of the absolute value of the input signal, and then computes
		the Spectral Coherence Function at a subset of them.
		Since there are modulations (such as OQPSK) that hide this information,
		we have to perform artificial shifts of I/Q values to check some
		different shifts and decide based on that.

		Parameters
		----------
		sig: np.ndarray
		input signal
		samp_rate: float
		(currently unused)
		debug: bool
		activate debug information/plots

		Returns
		-------
		sr: float
		estimated symbol rate (in normalized frequencies)
		"""
		N = iq_shifts_no
		sr = []
		for i in range(N):
				sr.append(tuple([0, 0]))

		# Parallelized execution of peak inspection.
		sr_vals = Parallel(n_jobs=num_cores)(delayed(inspect_single_shift)(w, sig, debug) for w in range(0, N))
		sr = [sr_vals[i][0] for i in range(len(sr_vals))]
		vals = np.array([sr_vals[i][1] for i in range(len(sr_vals))])
		idx_max = vals.argsort()[-3:][::-1]
		sr_max = np.array(sr)
		sr_max = sr_max[idx_max]

		all_sr = {sr.count(sr[i]): sr[i] for i in range(len(sr))}
		max_key = max(all_sr.keys())
		if debug:
				print("#### SR_VALS ####")
				print(sr_vals)
				print("#### SR ####")
				print(sr)
				print("#### VALS ####")
				print(vals)
				print("#### IDX_MAX ####")
				print(idx_max)
				print("#### ALL_SR ####")
				print(all_sr)
				print("#### max_key ####")
				print(max_key)
				logging.debug(all_sr)
				print(all_sr[max_key])

		est_sr = all_sr[max_key]

		return est_sr


def detection_analysis(x_chunks: np.ndarray, \
					   start_sample: int, \
					   det: Detection) -> None:
		r"""Callback function, in charge of analysing each individual detection.

		Parameters
		----------
		x_chunks: np.ndarray
		chunks of the input signal that we are considering for analysis
		start_sample: int
		absolute index of the start sample of the chunk (to de-relativise the
		sample indexes from signal chunks)
		det: Detection
		detection to process
		"""
		debug = False
		c_start_idx = int((det.start_sample - start_sample) / dt)
		c_end_idx = int((det.end_sample+1 - start_sample) / dt)
		x = x_chunks[c_start_idx:c_end_idx, :].flatten()
		y, _, _, _ = extract_signal(x.copy(), det.l_freq, det.h_freq, False)

		logging.info("-----------------------------------------------------\n" +
					 "Detection " + str(det.id) + ":\n" +
					 "\tstart_idx   = " + str(det.start_sample) +
					 "\n\tend_idx     = " + str(det.end_sample) +
					 "\n\tcenter freq = " +
					 str((det.h_freq+det.l_freq)/2) +
					 "\n\tfreq band   = [" + str(det.l_freq) +
					 ", " + str(det.h_freq) + "]")

		z = extract_signal_with_resampling(x.copy(),
										   det.l_freq,
										   det.h_freq,
										   debug)
		multicarrier_signal = is_multicarrier(z, debug)

		# If we just have Gaussian noise in our signal the check above (which
		# tests the Gaussianity) will return that we have a multicarrier signal.
		# It is thus worth checking whether we really have a MC signal or we are
		# just observing noise...
		# In a real multicarrier signal, we do expect to have a repetitive
		# pattern somewhere (synchronization symbols, guard intervals, ...). This
		# will not be the case for pure noise. We can thus autocorrelate the
		# signal and look for any pattern.
		if multicarrier_signal:
				if is_noise(y, debug):
						logging.debug("\n\tThe recorded signal looks like "
									 "multi-carrier, but no regularity has been"
									 "spotted -> noise !")
				else:
						logging.debug("\n\tMulti-carrier signal !")
		else:
				logging.debug("\n\tSingle-carrier signal !")
				sr = estimate_sr(y, fs, debug)
				logging.debug("######## Estimated symbol rate: " + str(sr))
