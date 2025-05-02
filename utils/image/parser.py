import json
import os
import re
from collections import namedtuple
from typing import List, Dict, NamedTuple

import piexif
import piexif.helper
from PIL import Image

from typing import NamedTuple, Optional

def get_img_geninfo_txt_path(path: str):
    txt_path = re.sub(r"\.\w+$", ".txt", path)
    if os.path.exists(txt_path):
        return txt_path

def read_sd_webui_gen_info_from_image(image: Image, path="") -> str:
    """
    Reads metadata from an image file.

    Args:
        image (PIL.Image.Image): The image object to read metadata from.
        path (str): Optional. The path to the image file. Used to look for a .txt file with additional metadata.

    Returns:
        str: The metadata as a string.
    """
    items = image.info or {}
    geninfo = items.pop("parameters", None)
    if "exif" in items:
        exif = piexif.load(items["exif"])
        exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b"")

        try:
            exif_comment = piexif.helper.UserComment.load(exif_comment)
        except ValueError:
            exif_comment = exif_comment.decode("utf8", errors="ignore")

        if exif_comment:
            items["exif comment"] = exif_comment
            geninfo = exif_comment

    if not geninfo and path:
        try:
            txt_path = get_img_geninfo_txt_path(path)
            if txt_path:
                with open(txt_path) as f:
                    geninfo = f.read()
        except Exception as e:
            pass

    return geninfo



re_param_code = r'\s*([\w ]+):\s*("(?:\\"[^,]|\\"|\\|[^\"])+"|[^,]*)(?:,|$)'
re_param = re.compile(re_param_code)
re_imagesize = re.compile(r"^(\d+)x(\d+)$")
re_lora_prompt = re.compile(r"<lora:([\w_\s.]+)(?::([\d.]+))+>", re.IGNORECASE)
re_lora_extract = re.compile(r"([\w_\s.]+)(?:\d+)?")
re_lyco_prompt = re.compile(r"<lyco:([\w_\s.]+):([\d.]+)>", re.IGNORECASE)
re_parens = re.compile(r"[\\/\[\](){}]+")
re_lora_white_symbol = re.compile(r">\s+")


def unique_by(seq, key=lambda x: x):
    seen = set()
    result = []
    for item in seq:
        val = key(item)
        if val not in seen:
            seen.add(val)
            result.append(item)
    return result


def unquote(s: str) -> str:
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1].replace('\\"', '"')
    return s

def lora_extract(lora: str):
    """
    Extracts the LoRA model name from a given string.

    This function is used to extract the model name from a LoRA model reference string,
    typically in the format <lora:model_name:weight>. It ignores the weight and returns
    the name of the model.

    Args:
        lora (str): A string representing a LoRA model reference, typically in the format
                    <lora:model_name:weight>.

    Returns:
        str: The name of the LoRA model.

    Example:
        lora_model = "<lora:style:0.8>"
        model_name = lora_extract(lora_model)
        print(model_name)  # Output: 'style'
    """
    res = re_lora_extract.match(lora)
    return res.group(1) if res else lora


def parse_prompt(x: str):
    x = re.sub(r'\sBREAK\s', ' , BREAK , ', x)
    x = re.sub(re_lora_white_symbol, "> , ", x)
    x = x.replace("，", ",").replace("-", " ").replace("_", " ")
    x = re.sub(re_parens, "", x)
    tag_list = [x.strip() for x in x.split(",")]
    res = []
    lora_list = []
    lyco_list = []
    for tag in tag_list:
        if len(tag) == 0:
            continue
        idx_colon = tag.find(":")
        if idx_colon != -1:
            if re.search(re_lora_prompt, tag):
                lora_res = re.search(re_lora_prompt, tag)
                lora_list.append(
                    {"name": lora_res.group(1), "value": float(lora_res.group(2))}
                )
            elif re.search(re_lyco_prompt, tag):
                lyco_res = re.search(re_lyco_prompt, tag)
                lyco_list.append(
                    {"name": lyco_res.group(1), "value": float(lyco_res.group(2))}
                )
            else:
                tag = tag[0:idx_colon]
                if len(tag):
                    res.append(tag.lower())
        else:
            res.append(tag.lower())
    return {"pos_prompt": res, "lora": lora_list, "lyco": lyco_list}



def parse_generation_parameters(x: str):
    """
    Parses the generation parameters from a string input and returns structured data.

    This function processes various generation parameters such as metadata, prompts,
    and model settings from the input string. It supports the conversion of string values
    into appropriate data types (e.g., integers, floats) and handles special cases like
    LoRA and Lyco model references.

    Args:
        x (str): The input string containing generation parameters. Expected to have metadata
                 and prompt data in a specific format.

    Returns:
        Dict: A dictionary containing the parsed data with the following structure:
            - 'meta' (dict): Metadata parameters like 'Steps', 'Seed', 'Sampler', etc.
            - 'pos_prompt' (List[str]): List of positive prompt tags.
            - 'lora' (List[Dict]): List of LoRA model names and weights.
            - 'lyco' (List[Dict]): List of Lyco model references and weights.
            - 'negative_prompt' (List[str]): List of negative prompts.

    Example:
        result = parse_generation_parameters("Steps: 20, Size-1: 1024, Seed: 12345, CFG scale: 7.0")
        print(result['meta']['Steps'])  # Output: 20
    """
    res = {}
    prompt = ""
    negative_prompt = ""
    done_with_prompt = False
    if not x:
        return {"meta": {}, "pos_prompt": [], "lora": [], "lyco": []}

    *lines, lastline = x.strip().split("\n")
    if len(re_param.findall(lastline)) < 3:
        lines.append(lastline)
        lastline = ""
    if len(lines) == 1 and lines[0].startswith("Postprocess"):  # 把上面改成<2应该也可以，当时不敢动
        lastline = lines[
            0
        ]  # 把Postprocess upscale by: 4, Postprocess upscaler: R-ESRGAN 4x+ Anime6B 推到res解析
        lines = []
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("Negative prompt:"):
            done_with_prompt = True
            line = line[16:].strip()

        if done_with_prompt:
            negative_prompt += ("" if negative_prompt == "" else "\n") + line
        else:
            prompt += ("" if prompt == "" else "\n") + line

    for k, v in re_param.findall(lastline):
        try:
            k = str(k)
            k = k.strip().lower().replace(" ", "_")
            if len(v) == 0:
                res[k] = v
                continue
            if v[0] == '"' and v[-1] == '"':
                v = unquote(v)

            m = re_imagesize.match(v)
            if m is not None:
                res[f"width"] = m.group(1)
                res[f"height"] = m.group(2)
            else:
                res[k] = v
        except Exception:
            print(f"Error parsing \"{k}: {v}\"")

    prompt_parse_res = parse_prompt(prompt)
    lora = prompt_parse_res["lora"]
    for k in res:
        k_s = str(k)
        if k_s.startswith("AddNet Module") and str(res[k]).lower() == "lora":
            model = res[k_s.replace("Module", "Model")]
            value = res.get(k_s.replace("Module", "Weight A"), "1")
            lora.append({"name": lora_extract(model), "value": float(value)})
    return {
        "meta": res,
        "pos_prompt": unique_by(prompt_parse_res["pos_prompt"]),
        "lora": unique_by(lora, lambda x: x["name"].lower()),
        "lyco": unique_by(prompt_parse_res["lyco"], lambda x: x["name"].lower()),
        "negative_prompt": negative_prompt.split(",")
    }


if __name__ == "__main__":
    from pprint import pprint
    # image = Image.open(r"D:\Program\SD Front\utils\image\cat\00001-2025-05-02-unknown-model.jpg")
    # print(read_sd_webui_gen_info_from_image(image))
    image_generation_data = parse_generation_parameters(read_sd_webui_gen_info_from_image(image))
    print(read_sd_webui_gen_info_from_image(image))
    pprint(image_generation_data)
