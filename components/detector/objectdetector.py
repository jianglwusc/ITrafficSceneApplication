from .registry import DETECTOR
import torch
import random
import numpy as np
from .base import BaseDetector
from matplotlib import pyplot as plt
import torchvision.transforms.functional as F
from .yolov3 import  get_yolov3,pad_to_square,resize,non_max_suppression,rescale_boxes


@DETECTOR.register_module
class Yolov3Detector(BaseDetector):

    def __init__(self,
                 device,
                 conf_thres = 0.8,
                 nms_thres=0.4,
                 img_size=416,
                 batch_size=1):
        """Yolov3目标探测网络
        Args:
            device (torch.device): 模型运行硬件 cuda or cpu
            conf_thres (float, optional): 目标置信度阈值. Defaults to 0.8.
            nms_thres (float, optional): 非极大值抑制阈值. Defaults to 0.4.
            img_size (int, optional): 网络输入大小. Defaults to 416.
            batch_size (int, optional): 批处理大小. Defaults to 1.
        """                 
        # 神经网络输入图像大小
        self.img_size = img_size
        # 置信度阈值
        self.conf_thres = conf_thres
        # 非极大值抑制阈值
        self.nms_thres = nms_thres
        #self._instanceLock =
        super(Yolov3Detector, self).__init__(
            model=get_yolov3(
                img_size=img_size,
                device=device
            ),
            device=device,
            batch_size=batch_size)


    def preprocessing(self, imgs):
        """
        将输入的图像列表处理为batch
        Args:
            imgs (list[PIL.Image]) or list[np.ndarray] : 长度应该与batch_size匹配

        Returns:
            imgs_batch (torch.Tensor) : torch.Tensor shape like [N,C,H,W]
        """
        imgs = super().preprocessing(imgs)
        imgs = [self.__yolov3_img_pre(img) for img in imgs]
        imgs = [torch.unsqueeze(img,0) for img in imgs]
        imgs_batch = torch.cat(imgs,0).to(self.device)
        return imgs_batch


    def __yolov3_img_pre(self,img):
        """
        将图像处理为网络可以接受的大小
        Args:
            img (): PIL.Image or np.ndarray

        Returns:
            torch.Tensor
        """
        img = F.to_tensor(img)
        # Pad to square resolution
        img, _ = pad_to_square(img, 0)
        # Resize
        img = resize(img, self.img_size)
        return img


    def afterprocessing(self, detections: torch.Tensor,shapes: list):
        """
        非极大值抑制和rescale
        Args:
            detections: 神经网络的输出

        Returns:results (list[bboxs]):非极大值抑制和rescale后的输出

        """
        # NMS
        detections = non_max_suppression(detections,self.conf_thres,self.nms_thres)
        # 非极大值抑制后可能出现没有任何目标被探测出
        results = [None for _ in range(len(detections))]
        for index,detections_for_one in enumerate(detections):
            if detections_for_one is None:
                # 没有探测到任何东西直接跳过
                continue
            if isinstance(shapes,list):
                detections_for_one = rescale_boxes(detections_for_one, self.img_size, shapes[index][:2])
            elif isinstance(shapes,tuple):
                detections_for_one = rescale_boxes(detections_for_one, self.img_size, shapes[:2])
            else:
                raise AssertionError("shapes的类型错误")
            result = []
            for x1, y1, x2, y2, obj_conf, cls_conf, cls_pred in detections_for_one:
                result.append([x1.item(), y1.item(), x2.item(), y2.item(), obj_conf.item(), cls_conf.item(), cls_pred.item()])
            results[index] = result
        return results
    
    

    def __call__(self, imgs: list,shapes: list, *args, **kwargs):
        """
        YoLov3前传函数
        Args:
            imgs: 图像list or 图像 np.ndarray len(imgs)一个与batch_size匹配 
            shapes: 对应图像列表中每个图像的shape 比如 [img1.shape,img2.shape,.....,img_n.shape]
                    如果可以肯定整个列表中图像shape都不会发生变化，那么直接输入一个图像的shape tuple即可　比如　(H,W,C)

        Returns:
            detections:探测到的bboxs_list 其长度为图像列表长度，每个其中的bboxs对应一个imgs中的图像中的目标bboxs

        """
        imgs_batch = self.preprocessing(imgs)
        with torch.no_grad():
            detections = self.model(imgs_batch)
        detections = self.afterprocessing(detections,shapes)
        return detections





