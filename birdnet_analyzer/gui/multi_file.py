import gradio as gr

import birdnet_analyzer.localization as loc
import birdnet_analyzer.gui.utils as gu
import birdnet_analyzer.gui.analysis as ga


OUTPUT_TYPE_MAP = {
    "Raven selection table": "table",
    "Audacity": "audacity",
    "R": "r",
    "CSV": "csv",
    "Kaleidoscope": "kaleidoscope",
}


def runBatchAnalysis(
    output_path,
    confidence,
    sensitivity,
    overlap,
    fmin,
    fmax,
    species_list_choice,
    species_list_file,
    lat,
    lon,
    week,
    use_yearlong,
    sf_thresh,
    custom_classifier_file,
    output_type,
    combine_tables,
    locale,
    batch_size,
    threads,
    input_dir,
    skip_existing,
    progress=gr.Progress(),
):
    gu.validate(input_dir, loc.localize("validation-no-directory-selected"))
    batch_size = int(batch_size)
    threads = int(threads)

    if species_list_choice == gu._CUSTOM_SPECIES:
        gu.validate(species_list_file, loc.localize("validation-no-species-list-selected"))

    return ga.runAnalysis(
        None,
        output_path,
        confidence,
        sensitivity,
        overlap,
        fmin,
        fmax,
        species_list_choice,
        species_list_file,
        lat,
        lon,
        week,
        use_yearlong,
        sf_thresh,
        custom_classifier_file,
        output_type,
        combine_tables,
        "en" if not locale else locale,
        batch_size if batch_size and batch_size > 0 else 1,
        threads if threads and threads > 0 else 4,
        input_dir,
        skip_existing,
        progress,
    )


def build_multi_analysis_tab():
    with gr.Tab(loc.localize("multi-tab-title")):
        input_directory_state = gr.State()
        output_directory_predict_state = gr.State()

        with gr.Row():
            with gr.Column():
                select_directory_btn = gr.Button(loc.localize("multi-tab-input-selection-button-label"))
                directory_input = gr.Matrix(
                    interactive=False,
                    elem_classes="matrix-mh-200",
                    headers=[
                        loc.localize("multi-tab-samples-dataframe-column-subpath-header"),
                        loc.localize("multi-tab-samples-dataframe-column-duration-header"),
                    ],
                )

                def select_directory_on_empty():  # Nishant - Function modified for For Folder selection
                    folder = gu.select_folder(state_key="batch-analysis-data-dir")

                    if folder:
                        files_and_durations = gu.get_files_and_durations(folder)
                        if len(files_and_durations) > 100:
                            return [folder, files_and_durations[:100] + [["..."]]]  # hopefully fixes issue#272
                        return [folder, files_and_durations]

                    return ["", [[loc.localize("multi-tab-samples-dataframe-no-files-found")]]]

                select_directory_btn.click(
                    select_directory_on_empty, outputs=[input_directory_state, directory_input], show_progress=True
                )

            with gr.Column():
                select_out_directory_btn = gr.Button(loc.localize("multi-tab-output-selection-button-label"))
                selected_out_textbox = gr.Textbox(
                    label=loc.localize("multi-tab-output-textbox-label"),
                    interactive=False,
                    placeholder=loc.localize("multi-tab-output-textbox-placeholder"),
                )

                def select_directory_wrapper():  # Nishant - Function modified for For Folder selection
                    folder = gu.select_folder(state_key="batch-analysis-output-dir")
                    return (folder, folder) if folder else ("", "")

                select_out_directory_btn.click(
                    select_directory_wrapper,
                    outputs=[output_directory_predict_state, selected_out_textbox],
                    show_progress=False,
                )

        confidence_slider, sensitivity_slider, overlap_slider, fmin_number, fmax_number = gu.sample_sliders()

        (
            species_list_radio,
            species_file_input,
            lat_number,
            lon_number,
            week_number,
            sf_thresh_number,
            yearlong_checkbox,
            selected_classifier_state,
        ) = gu.species_lists()

        with gr.Accordion(loc.localize("multi-tab-output-accordion-label"), open=True):
            output_type_radio = gr.CheckboxGroup(
                list(OUTPUT_TYPE_MAP.items()),
                value="table",
                label=loc.localize("multi-tab-output-radio-label"),
                info=loc.localize("multi-tab-output-radio-info"),
            )

            with gr.Row():
                with gr.Column():
                    combine_tables_checkbox = gr.Checkbox(
                        False,
                        label=loc.localize("multi-tab-output-combine-tables-checkbox-label"),
                        info=loc.localize("multi-tab-output-combine-tables-checkbox-info"),
                    )

            with gr.Row():
                skip_existing_checkbox = gr.Checkbox(
                    False,
                    label=loc.localize("multi-tab-skip-existing-checkbox-label"),
                    info=loc.localize("multi-tab-skip-existing-checkbox-info"),
                )

        with gr.Row():
            batch_size_number = gr.Number(
                precision=1,
                label=loc.localize("multi-tab-batchsize-number-label"),
                value=1,
                info=loc.localize("multi-tab-batchsize-number-info"),
                minimum=1,
            )
            threads_number = gr.Number(
                precision=1,
                label=loc.localize("multi-tab-threads-number-label"),
                value=4,
                info=loc.localize("multi-tab-threads-number-info"),
                minimum=1,
            )

        locale_radio = gu.locale()

        start_batch_analysis_btn = gr.Button(loc.localize("analyze-start-button-label"))

        result_grid = gr.Matrix(
            headers=[
                loc.localize("multi-tab-result-dataframe-column-file-header"),
                loc.localize("multi-tab-result-dataframe-column-execution-header"),
            ],
            elem_classes="matrix-mh-200",
        )

        inputs = [
            output_directory_predict_state,
            confidence_slider,
            sensitivity_slider,
            overlap_slider,
            fmin_number,
            fmax_number,
            species_list_radio,
            species_file_input,
            lat_number,
            lon_number,
            week_number,
            yearlong_checkbox,
            sf_thresh_number,
            selected_classifier_state,
            output_type_radio,
            combine_tables_checkbox,
            locale_radio,
            batch_size_number,
            threads_number,
            input_directory_state,
            skip_existing_checkbox,
        ]

        start_batch_analysis_btn.click(runBatchAnalysis, inputs=inputs, outputs=result_grid)


if __name__ == "__main__":
    gu.open_window(build_multi_analysis_tab)
