import torch
from transformers import AutoModelForImageTextToText, AutoProcessor
from chandra.model.hf import generate_hf
from chandra.model.schema import BatchInputItem
from chandra.output import parse_markdown
from PIL import Image

class Scanner():
    model=None
    def loadModel(cls):
        cls.model = AutoModelForImageTextToText.from_pretrained(
            "datalab-to/chandra-ocr-2",
            dtype=torch.bfloat16,
            device_map="auto",
        )
        print(torch.cuda.get_device_name(0))

    def scan(cls, path):
        if cls.model == None:
            cls.loadModel()

        image = Image.open(path).convert("RGB")
        max_size = 1540 
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.LANCZOS)

        cls.model.eval()
        cls.model.processor = AutoProcessor.from_pretrained("datalab-to/chandra-ocr-2")
        cls.model.processor.tokenizer.padding_side = "left"

        batch = [
            BatchInputItem(
                image=image,
                prompt_type="ocr_layout"
            )
        ]

        result = generate_hf(batch, cls.model)[0]
        markdown = parse_markdown(result.raw)
        return(markdown)

#ocr = Scanner()
#ocr.scan("/home/mc/Projects/OCRshit/upscaled_pages/upscaled_Patrologiæ_cursus_completus_part_1_27.png")