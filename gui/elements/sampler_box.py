from PySide6.QtCore import Qt

from gui.common import GridFrame
from gui.common.card import FlowTitleCard
from gui.components import ComboBoxCard, SliderCard, CheckBoxCard, DoubleSliderCard
from api import sd_api_manager


class SamplerBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(spacing= 6, parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setColumnCount(2)  # 2 columns layout

        self.samplers = ComboBoxCard(
            "Sampling Algorithm",
            description="""Choose the denoising method that affects quality and speed:
            - Euler: Fastest, good for quick iterations
            - DPM++ 2M: Balanced quality/speed (recommended)
            - LMS Karras: Smooth gradients, great for portraits
            - DPM Adaptive: Auto-adjusts steps for consistent quality
            - Heun: Highest quality but 2x slower
            Tip: Start with DPM++ 2M Karras for most use cases""",
            show_info_on_focus=True,
            parent=self
        )

        self.steps = SliderCard(
            "Steps",
            description="""Control how many times the image gets refined:
            10-20: Draft quality (fast previews)
            20-30: Standard quality
            30-50: High quality (recommended for final output)
            50+: Diminishing returns
            Note: More steps require exponentially more time""",
            show_info_on_focus=True,
            parent=self
        )
        self.steps.set_range(10, 100)
        self.steps.set_value(30)

        self.sigma_method = ComboBoxCard(
            "Sigma Method",
            description="""How noise is reduced over time:
            - Exponential: Aggressive early, gentle late
            - Linear: Consistent reduction (default)
            - Karras: Sharpens details in final steps
            - V-Explosion: Preserves mid-process details
            For photorealism: Karras
            For art: Exponential""",
            show_info_on_focus=True,
            parent=self
        )

        self.beta_schedule = ComboBoxCard(
            "Beta Scheduler",
            description="""Controls noise progression:
            - Linear: Predictable results
            - Scaled Linear: Better for high steps
            - Sqrt: More early-stage creativity
            - Cosine: Smooth transitions (good for faces)
            Stick with Linear unless you need specific effects""",
            show_info_on_focus=True,
            parent=self
        )

        self.timestep_spacing = ComboBoxCard(
            "Timestep Spacing",
            description="""How steps are distributed:
            - Uniform: Equal spacing (default)
            - Leading: More early refinement
            - Trailing: More late refinement
            - Karras: Focused on critical phases
            Use Leading for conceptual work, Trailing for polishing""",
            show_info_on_focus=True,
            parent=self
        )

        self.prediction_method = ComboBoxCard(
            "Prediction Method",
            description="""How the model interprets noise:
            - EPS: Standard approach
            - V-Prediction: Better for latent space
            - Sample: Good for high CFG scales
            - Original: Legacy mode
            EPS works for 90% of cases""",
            show_info_on_focus=True,
            parent=self
        )


        self.sigma_adjust = DoubleSliderCard(
            "Sigma Adjustment",
            description="""Fine-tune the noise profile:
            0.8-1.0: Less aggressive (preserves structure)
            1.0: Default
            1.0-1.2: More aggressive (creative changes)
            Useful for fixing over/under processed areas""",
            show_info_on_focus=True,
            parent=self
        )
        self.sigma_adjust.set_range(0, 2, 1)
        self.sigma_adjust.set_value(1)

        self.adjust_start = DoubleSliderCard(
            "Adjust Start",
            description="""When initial adjustments begin:
            0.0-0.3: Immediate refinement
            0.3-0.6: Balanced approach
            0.6-1.0: Late-stage tweaks
            Lower values help with major composition changes""",
            show_info_on_focus=True,
            parent=self
        )
        self.adjust_start.set_range(0, 1, 2)
        self.adjust_start.set_value(0.2)

        self.adjust_end = DoubleSliderCard(
            "Adjust End",
            description="""When final refinements occur:
            0.0-0.3: Early completion
            0.3-0.7: Standard workflow
            0.7-1.0: Last-moment tweaks
            Higher values preserve early creativity""",
            show_info_on_focus=True,
            parent=self
        )
        self.adjust_end.set_range(0, 1, 2)
        self.adjust_end.set_value(0.8)

        self.sampler_order = SliderCard(
            "Sampler Order",
            description="""Adjust the order of sampling:
            0: Standard (default)
            1: Early refinement
            2: Late refinement
            3: Creative variations
            4: Batched processing
            5: Optimized sequence
            Adjust to prioritize certain aspects""",
            show_info_on_focus=True,
            parent=self
        )
        self.sampler_order.set_range(0, 5)
        self.sampler_order.set_value(4)

        self.flow_shift = DoubleSliderCard(
            "Flow Shift",
            description="""For video/animation frames:
            0: No smoothing between frames
            0.1-0.3: Subtle continuity (recommended)
            0.3-0.5: Strong frame blending
            Higher values reduce flickering but may cause motion blur""",
            show_info_on_focus=True,
            parent=self
        )
        self.flow_shift.set_range(0, 10, 1)
        self.flow_shift.set_value(3)



        # Add widgets one after another (auto grid logic handles placement)
        for widget in [
            self.samplers, self.steps, self.sigma_method, self.beta_schedule,
            self.prediction_method, self.timestep_spacing, self.sigma_adjust, self.adjust_start,
            self.adjust_end, self.sampler_order,
        ]:
            self.addWidget(widget)

        self.addFullWidthWidget(self.flow_shift)

        #options
        container = FlowTitleCard("Options")
        self.low_order = CheckBoxCard("Low Order")
        self.low_order.setChecked(True)
        self.thresholding = CheckBoxCard("Thresholding")
        self.dynamic = CheckBoxCard("Dynamic")
        self.rescale = CheckBoxCard("Rescale")
        options = ["low order", "thresholding", "dynamic", "rescale"]

        container.addWidget(self.low_order)
        container.addWidget(self.thresholding)
        container.addWidget(self.dynamic)
        container.addWidget(self.rescale)

        self.addFullWidthWidget(container)

        sd_api_manager.sampler_fetched.connect(self.set_samplers)

    def get_payload(self) -> dict:
        return {
            "sampler_name": self.samplers.currentText(),
            "steps": self.steps.value(),
            "sigma_schedule": self.sigma_method.currentText(),
            "beta_schedule": self.beta_schedule.currentText(),
            "timestep_spacing": self.timestep_spacing.currentText(),
            "prediction_type": self.prediction_method.currentText(),
            "sampler_order": self.sampler_order.value(),
            "pag_scale": self.sigma_adjust.value(),
            "pag_adaptive": {
                "start": self.adjust_start.value(),
                "end": self.adjust_end.value()
            },
            "flow_shift": self.flow_shift.value()
        }

    def set_payload(self, data: dict):
        """Populates the UI from a dict."""
        if not isinstance(data, dict):
            return

        self.samplers.setCurrentText(data.get("sampler_name", self.samplers.currentText()))
        self.steps.setValue(data.get("steps", self.steps.value()))
        self.sigma_method.setCurrentText(data.get("sigma_schedule", self.sigma_method.currentText()))
        self.beta_schedule.setCurrentText(data.get("beta_schedule", self.beta_schedule.currentText()))
        self.timestep_spacing.setCurrentText(data.get("timestep_spacing", self.timestep_spacing.currentText()))
        self.prediction_method.setCurrentText(data.get("prediction_type", self.prediction_method.currentText()))
        self.sampler_order.setValue(data.get("sampler_order", self.sampler_order.value()))
        self.sigma_adjust.setValue(data.get("pag_scale", self.sigma_adjust.value()))
        self.flow_shift.setValue(data.get("flow_shift", self.flow_shift.value()))

        pag_adaptive = data.get("pag_adaptive", {})
        if isinstance(pag_adaptive, dict):
            self.adjust_start.setValue(pag_adaptive.get("start", self.adjust_start.value()))
            self.adjust_end.setValue(pag_adaptive.get("end", self.adjust_end.value()))

    def set_samplers(self, samplers: list[dict]):
        self.samplers.clear()
        for sampler in samplers:
            self.samplers.comboBox.addItem(sampler["name"])

# self.addWidget(widget, alignment=Qt.AlignTop)  # Align each widget to the top

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = SamplerBox()
    window.show()
    # window.set_payload({
    #     "sampler_name": "DPM++ 2M Karras",
    #     "steps": 30,
    #     "sigma_schedule": "Karras",
    #     "beta_schedule": "Linear",
    #     "timestep_spacing": "Leading",
    #     "prediction_type": "EPS",
    #     "sample_order": "Sequential",
    #     "pag_scale": 1.0,
    #     "pag_adaptive": {
    #         "start": 0.6,
    #         "end": 0.7
    #     },
    #     "flow_shift": 0.3
    # })
    print(window.get_payload())
    sd_api_manager.fetch_sampler()
    app.exec()

