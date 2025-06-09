import os
from textfsm import clitable
from textfsm.clitable import CliTableError
from pathlib import Path
from typing import Any, Callable, Optional, Union


def structured_data_converter(
    raw_data: str, command: str, platform: str, textfsm_template: Optional[str] = None
) -> Union[str, list[Any], dict[str, Any]]:
    """
    TextFSMテンプレートを利用してデータを加工し返却
    """
    command = command.strip()
    structured_output_tfsm = get_structured_data_textfsm(
        raw_data, platform=platform, command=command, template=textfsm_template
    )
    if not isinstance(structured_output_tfsm, str):
        return structured_output_tfsm

    return raw_data


def get_structured_data_textfsm(
    raw_output: str,
    platform: Optional[str] = None,
    command: Optional[str] = None,
    template: Optional[str] = None,
) -> Union[str, list[dict[str, str]]]:
    if platform is None or command is None:
        attrs = {}
    else:
        attrs = {"Command": command, "Platform": platform}

    if template is None:
        if attrs == {}:
            raise ValueError(
                "Either 'platform/command' or 'template' must be specified."
            )

        template_dir = get_template_dir()
        index_file = os.path.join(template_dir, "index")
        textfsm_obj = clitable.CliTable(index_file, template_dir)
        output = _textfsm_parse(textfsm_obj, raw_output, attrs)

        if platform and "cisco_xe" in platform:
            if not isinstance(output, list):
                attrs["Platform"] = "cisco_ios"
                output = _textfsm_parse(textfsm_obj, raw_output, attrs)

        return output

    else:
        template_path = Path(os.path.expanduser(template))
        template_file = template_path.name
        template_dir_alt = template_path.parents[0]
        textfsm_obj = clitable.CliTable(template_dir=template_dir_alt)

        return _textfsm_parse(
            textfsm_obj, raw_output, attrs, template_file=template_file
        )


def _textfsm_parse(
    textfsm_obj: clitable.CliTable,
    raw_output: str,
    attrs: dict[str, str],
    template_file: Optional[str] = None,
) -> Union[str, list[dict[str, str]]]:
    tfsm_parse: Callable[..., Any] = textfsm_obj.ParseCmd
    try:
        if template_file is not None:
            tfsm_parse(raw_output, templates=template_file)
        else:
            tfsm_parse(raw_output, attrs)

        structured_data = clitable_to_dict(textfsm_obj)
        if structured_data == []:
            return raw_output
        else:
            return structured_data

    except (FileNotFoundError, CliTableError):
        return raw_output


def clitable_to_dict(cli_table: clitable.CliTable) -> list[dict[str, str]]:
    return_list = []
    for row in cli_table:
        temp_dict = {}
        for index, element in enumerate(row):
            temp_dict[cli_table.header[index].lower()] = element
        return_list.append(temp_dict)

    return return_list


def get_template_dir(_skip_ntc_package: bool = False) -> str:
    msg = """
Directory containing TextFSM index file not found.

Please set the NET_TEXTFSM environment variable to point at the directory containing your TextFSM
index file.

Alternatively, `pip install ntc-templates` (if using ntc-templates).

"""

    template_dir = os.environ.get("NET_TEXTFSM")
    if template_dir is not None:
        template_dir = os.path.expanduser(template_dir)
        index = os.path.join(template_dir, "index")
        if not os.path.isfile(index):
            template_dir = os.path.join(template_dir, "templates")

    else:
        try:
            raise ModuleNotFoundError()

        except ModuleNotFoundError:
            home_dir = os.path.expanduser("~")
            template_dir = os.path.join(
                home_dir, "ntc-templates", "ntc_templates", "templates"
            )

    index = os.path.join(template_dir, "index")
    if not os.path.isdir(template_dir) or not os.path.isfile(index):
        raise ValueError(msg)
    return os.path.abspath(template_dir)
