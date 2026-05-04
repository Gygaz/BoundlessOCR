import cv2
import os
import gc
import torch
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

class Upscaler:
    scale=4

    @classmethod
    def set_scale(cls, number):
        cls.scale = number

    @classmethod
    def setup_upscaler(cls, model_path=None):

        if hasattr(cls, 'upsampler'):
            del cls.upsampler
        gc.collect()
        torch.cuda.empty_cache()

        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=cls.scale)
       
        upsampler = RealESRGANer(
            scale=cls.scale,
            model_path=model_path,
            model=model,
            tile=400,
            tile_pad=10,
            pre_pad=0,
            half=False
        )
        return upsampler

    @classmethod
    def process_image(cls, upsampler, input_path, output_path, wanted_resolution):
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        output, _ = upsampler.enhance(img, outscale=cls.scale)

        target_width=wanted_resolution
        scale = target_width/output.shape[1]
        
        if scale !=1:
            new_height = int(output.shape[0] * scale)  
            resized_img = cv2.resize(output, (target_width, new_height), interpolation=cv2.INTER_AREA)  
            output=resized_img  

        cv2.imwrite(output_path, output)