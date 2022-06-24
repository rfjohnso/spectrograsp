import numpy as np


class Detection:

		def __init__(self, id: int, start_sample: int, l_freq: float, h_freq: float) -> None:
				r"""Initialize a Detection.

				Parameters
				----------
				id: int
				Detection ID
				start_sample: int
				Starting sample position for the detection (in time domain)
				l_freq: float
				Lower bound of the signal in the frequency domain (in normalized frequencies)
				h_freq: float
				Upper bound of the signal in the frequency domain (in normalized frequencies)
				"""
				# Ending sample position for the detection (in time domain).
				self.end_sample: int = -1
				# Associated signal chunk.
				self.x: np.complex_
				# List of associated frequencies (in chronological order).
				self.freqs = list()
				self.freqs.append([l_freq, h_freq])
				self.id = id
				self.start_sample: int = start_sample

		def __str__(self):
				r"""Describe a Detection as a string, which is returned to the caller.
				"""
				return u"Detection %d: start sample = %d, end sample = %d, init lower freq = %.3f, " \
						"init upper freq = %.3f, CENTER freq = %.3f" % \
						(self.id, self.start_sample, self.end_sample, self.freqs[0][0], self.freqs[0][1],
						 (self.freqs[0][1] + self.freqs[0][0]) / 2)

		def append_detection(self, l_freq: float, h_freq: float) -> None:
				r"""Add a new position in the frequency domain

				Parameters
				----------
				l_freq: float
				Lower bound of the signal in the frequency domain (in normalized frequencies)
				h_freq: float
				Upper bound of the signal in the frequency domain (in normalized frequencies)
				"""
				self.freqs.append([l_freq, h_freq])

		def get_last_lfreq(self) -> float:
				r"""Get the lower frequency of the latest detection.

				Returns
				-------
				l_freq: float
				Lower bound of the signal in the frequency domain (in normalized frequencies) for the last detection.
				"""
				return self.freqs[-1][0]

		def get_last_hfreq(self) -> float:
				r"""Get the upper frequency of the latest detection.

				Returns
				-------
				h_freq: float
				Upper bound of the signal in the frequency domain (in normalized frequencies) for the last detection.
				"""
				return self.freqs[-1][1]

		def set_end(self, end_idx: int, x_chunk: np.complex_) -> None:
				r"""Set the detection's endpoint, as well as store the associated signal block.

				Parameters
				----------
				end_sample: int
				Ending sample position for the detection (in time domain)
				x: np.complex_
				Signal chunk
				"""
				# print("Set DETECTION END: " + str(end_sample) + " for detection: " + str(id))
				self.end_sample = end_idx
				self.x = x_chunk

		def average_frequencies(self) -> None:
				r"""Go over the observed frequencies and take the mean value for
				both the upper and the lower frequency.
				"""
				self.l_freq = 0
				self.h_freq = 0
				N = len(self.freqs)
				assert (N > 0)
				# for f in range(N):
				# 		self.l_freq += self.freqs[f][0]
				# 		self.h_freq += self.freqs[f][1]
				# self.l_freq /= N
				# self.h_freq /= N
				self.l_freq = self.freqs[0][0]
				self.h_freq = self.freqs[0][1]
				for f in range(1, N):
						self.l_freq = min(self.l_freq, self.freqs[f][0])
						self.h_freq = max(self.h_freq, self.freqs[f][1])
