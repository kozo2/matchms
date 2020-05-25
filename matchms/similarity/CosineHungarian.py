import numba
import numpy
from scipy.optimize import linear_sum_assignment
from matchms.typing import SpectrumType


class CosineHungarian:
    """Calculate cosine score between two spectra using the Hungarian algorithm.

    This score is calculated by summing intensiy products of matching peaks between
    two spectra (matching within set tolerance).
    of two spectra.

    Args:
    ----
    tolerance: float
        Peaks will be considered a match when <= tolerance appart. Default is 0.1.
    """
    def __init__(self, tolerance=0.1):
        self.tolerance = tolerance

    def __call__(self, spectrum1: SpectrumType, spectrum2: SpectrumType) -> float:
        """Calculate cosine score between two spectra.
        Args:
        ----
        spectrum1: SpectrumType
            Input spectrum 1.
        spectrum2: SpectrumType
            Input spectrum 2.
        """
        def get_peaks_arrays():
            """Get peaks mz and intensities as numpy array."""
            spec1 = numpy.vstack((spectrum1.peaks.mz, spectrum1.peaks.intensities)).T
            spec2 = numpy.vstack((spectrum2.peaks.mz, spectrum2.peaks.intensities)).T
            assert max(spec1[:, 1]) <= 1, ("Input spectrum1 is not normalized. ",
                                           "Apply 'normalize_intensities' filter first.")
            assert max(spec2[:, 1]) <= 1, ("Input spectrum2 is not normalized. ",
                                           "Apply 'normalize_intensities' filter first.")
            return spec1, spec2

        def get_matching_pairs():
            """Get pairs of peaks that match within the given tolerance."""
            matching_pairs = find_pairs_numba(spec1, spec2, self.tolerance, shift=0.0)
            matching_pairs = sorted(matching_pairs, key=lambda x: x[2], reverse=True)
            return matching_pairs

        def calc_score():
            """Calculate cosine similarity score."""
            used_matches = []
            list1 = list({x[0] for x in matching_pairs})
            list2 = list({x[1] for x in matching_pairs})
            matrix_size = (len(list1), len(list2))
            matrix = numpy.ones(matrix_size)

            if len(matching_pairs) > 0:
                for match in matching_pairs:
                    matrix[list1.index(match[0]), list2.index(match[1])] = 1 - match[2]
                # Use hungarian agorithm to solve the linear sum assignment problem
                row_ind, col_ind = linear_sum_assignment(matrix)
                score = len(row_ind) - matrix[row_ind, col_ind].sum()
                used_matches = [(list1[x], list2[y]) for (x, y) in zip(row_ind, col_ind)]
                # Normalize score:
                score = score/max(numpy.sum(spec1[:, 1]**2), numpy.sum(spec2[:, 1]**2))
            else:
                score = 0.0
            return score, len(used_matches)

        spec1, spec2 = get_peaks_arrays()
        matching_pairs = get_matching_pairs()
        return calc_score()


@numba.njit
def find_pairs_numba(spec1, spec2, tolerance, shift=0):
    """Find matching pairs between two spectra.

    Args
    ----
    spec1: numpy array
        Spectrum peaks and intensities as numpy array.
    spec2: numpy array
        Spectrum peaks and intensities as numpy array.
    tolerance : float
        Peaks will be considered a match when <= tolerance appart.
    shift : float, optional
        Shift spectra peaks by shift. The default is 0.

    Returns
    -------
    matching_pairs : list
        List of found matching peaks.
    """
    matching_pairs = []

    for idx in range(len(spec1)):
        intensity = spec1[idx, 1]
        matches = numpy.where((numpy.abs(spec2[:, 0] - spec1[idx, 0] + shift) <= tolerance))[0]
        for match in matches:
            matching_pairs.append((idx, match, intensity*spec2[match][1]))

    return matching_pairs
