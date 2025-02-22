from dataclasses import dataclass


@dataclass
class FormUI:
    title: str

    @dataclass
    class SubmitButton:
        text: str

    submit_button: SubmitButton


@dataclass
class MessageUI:
    title: str
    message: str
