from matchms.filtering import *


class SpectrumProcessor:
    """
    A class to process spectra using a series of filters. 

    The class enables a user to define a custom spectrum processing workflow by setting multiple
    flags and parameters.

    Parameters
    ----------
    processing_pipeline : str
        Name of a predefined processing pipeline. Options: 'minimal', 'basic', 'default',
        'fully_annotated'.
    """

    def __init__(self, processing_pipeline='default'):
        if processing_pipeline not in PREDEFINED_PIPELINES:
            raise ValueError(f"Unknown processing pipeline '{processing_pipeline}'. Available pipelines: {list(PREDEFINED_PIPELINES.keys())}")
        
        self.filters = []
        for fname in PREDEFINED_PIPELINES[processing_pipeline]:
            self.add_filter(fname)

    def add_filter(self, filter_spec):
        """
        Add a filter to the processing pipeline.

        Parameters
        ----------
        filter_spec : str or tuple
            Name of the filter function to add, or a tuple where the first element is the name of the 
            filter function and the second element is a dictionary containing additional arguments for the function.
        """
        if isinstance(filter_spec, str):
            filter_func = FILTER_FUNCTIONS[filter_spec]
            self.filters.append(filter_func)
        elif isinstance(filter_spec, tuple):
            filter_name, filter_args = filter_spec
            filter_func = FILTER_FUNCTIONS[filter_name]
            self.filters.append(lambda spectrum: filter_func(spectrum, **filter_args))
        else:
            raise TypeError("filter_spec should be a string or a tuple")

        # Sort filters according to their order in ALL_FILTERS
        self.filters.sort(key=lambda f: ALL_FILTERS.index(f))
        return self

    def process_spectrum(self, spectrum):
        """
        Process the given spectrum with all filters in the processing pipeline.

        Parameters
        ----------
        spectrum : Spectrum
            The spectrum to process.
        
        Returns
        -------
        Spectrum
            The processed spectrum.
        """
        for filter_func in self.filters:
            spectrum = filter_func(spectrum)
            if spectrum is None:
                break
        return spectrum


# List all filters in a functionally working order
ALL_FILTERS = [make_charge_int,
               add_compound_name,
               derive_adduct_from_name,
               derive_formula_from_name,
               clean_compound_name,
               interpret_pepmass,
               add_precursor_mz,
               add_retention_index,
               add_retention_time,
               derive_ionmode,
               correct_charge,
               derive_adduct_from_name,  # run again
               derive_formula_from_name,  # run again
               require_precursor_mz,
               add_parent_mass,
               harmonize_undefined_inchikey,
               harmonize_undefined_inchi,
               harmonize_undefined_smiles,
               repair_inchi_inchikey_smiles,
               repair_parent_mass_match_smiles_wrapper,
               require_correct_ionmode,
               require_precursor_below_mz,
               require_parent_mass_match_smiles,
               require_valid_annotation,
               normalize_intensities,
               select_by_intensity,
               select_by_mz,
               select_by_relative_intensity,
               remove_peaks_around_precursor_mz,
               remove_peaks_outside_top_k,
               require_minimum_number_of_peaks,
               require_minimum_of_high_peaks,
               add_fingerprint,
               add_losses,
              ]

FILTER_FUNCTIONS = {x.__name__: x for x in ALL_FILTERS}

MINIMAL_FILTERS = ["make_charge_int",
                   "interpret_pepmass",
                   "derive_ionmode",
                   "correct_charge",
                   ]
BASIC_FILTERS = MINIMAL_FILTERS \
    + ["derive_adduct_from_name",
       "derive_formula_from_name",
       "clean_compound_name",
       "interpret_pepmass",
       "add_precursor_mz",
    ]
DEFAULT_FILTERS = BASIC_FILTERS \
    + ["require_precursor_mz",
       "add_parent_mass",
       "harmonize_undefined_inchikey",
       "harmonize_undefined_inchi",
       "harmonize_undefined_smiles",
       "repair_inchi_inchikey_smiles",
       "repair_parent_mass_match_smiles_wrapper",
       "require_correct_ionmode",
       "normalize_intensities",
    ]
FULLY_ANNOTATED_PROCESSING = DEFAULT_FILTERS \
    + ["require_parent_mass_match_smiles",
       "require_valid_annotation",
    ]

PREDEFINED_PIPELINES = {
    "minimal": MINIMAL_FILTERS,
    "basic": BASIC_FILTERS,
    "default": DEFAULT_FILTERS,
    "fully_annotated": FULLY_ANNOTATED_PROCESSING,
}
