import cv2
import mmcv
import os
import json
import torch
import os.path as osp
import numpy as np
from copy import deepcopy
from cfg import TaskConfig
from cfg import DataConfig
from utils.utils import draw_mask
TaskCfg = {
    'task_name': '路口交通场景',
    'head':
        {
            'type': 'VideoFileHead',
            'filename': None,
            'step': TaskConfig.BATCH_SIZE,
            'cache_capacity': 100
        }
    ,
    'detector': 
        {
            'type': 'Yolov5Detector',
            'device': '0',
            'batch_size': TaskConfig.BATCH_SIZE,
            'weights':'./components/detector/yolov5/weights/yolov5s.pt'
        }
    ,
    'tracker':
        {
            'type': 'SORT_Track'
        }
    ,
    'backbones': [
        [
            # fps计数组件
            {
                'type': 'FpsCollectorComponent',
                'isPrint': TaskConfig.IS_PRINT_FPS
            },
            {
                'type': 'PathExtract',   # 路径分析模块，基础模块，不可或缺
                'eModelPath':None #视频环境模型路径，必须赋值
            },
            {
                'type': 'TrafficStatistics',     # 车流统计模块
                'eModelPath': None, #视频环境模型路径，必须赋值
                'is_process':False # 是否开启该组件
            },
            {
                'type': 'ParkingMonitoringComponent', # 违章停车监控组件
                'monitoring_area': None, # 监控区域，必须赋值
                'allow_stop_time': TaskConfig.ALLOW_STOP_TIME,
                'is_process':False # 是否开启该组件
            },
            {
                'type': 'LaneMonitoringComponent', # 违法占用车道组件
                'monitoring_area':None,  # 监控区域，必须赋值
                'no_allow_car':None, # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
                'is_process':False # 是否开启该组件
            },
            {
                'type': 'PersonMonitoringComponent', # 违章停车监控组件
                'monitoring_area': None, # 监控区域，必须赋值
                'is_process':False # 是否开启该组件
            },
            # 数据库写入组件
            {
                'type': 'InformationCollectorComponent',
            },
            {
              'type': 'DrawBoundingBoxComponent'  # 画框框
            },
            {
                'type': 'RtmpWriteComponent',
                'resolution': (1920, 1080),
                'fps': 30,
                'rtmpUrl': TaskConfig.RTMP_URL
            }

        ]
    ]
}

def get_injected_cfg(cfg_data):
    if 'filename' not in cfg_data.keys():
        raise RuntimeError('注入数据必须指定filename参数，以确定处理的数据。')
    filename = cfg_data['filename']
    filepath = osp.join(DataConfig.VIDEO_DIR, filename)
    if not osp.exists(filepath):
        raise RuntimeError('文件夹{}中不存在名字为{}的视频或者视频源头'.format(DataConfig.VIDEO_DIR, filename))
    taskCfg = deepcopy(TaskCfg)
    taskCfg['head']['filename'] = filepath
    # jsonname = filename.split('.')[0]+'.json'
    # jsonpath = osp.join(DataConfig.JSON_DIR,jsonname)
    # taskCfg['head']['json_filename'] = jsonpath
    emodelname = filename.split('.')[0] + '.emd'
    emodelpath = osp.join(DataConfig.EMODEL_DIR, emodelname)
    if not osp.exists(emodelpath):
        raise RuntimeError('文件夹{}中不存在名字为{}的环境模型,请先执行建模Task'.format(DataConfig.EMODEL_DIR, emodelname))
    taskCfg['backbones'][0][1]['eModelPath'] = emodelpath
    taskCfg['backbones'][0][2]['eModelPath'] = emodelpath
    taskCfg['backbones'][0][2]['is_process'] = True
    if 'parking_monitoring_area' in cfg_data.keys():
        all_point_array = [np.array(x, dtype=np.int32) for x in cfg_data['parking_monitoring_area']]
        mask = np.ones_like(mmcv.VideoReader(filepath)[10][:,:,0])
        parking_mask = cv2.fillPoly(mask, all_point_array, 0)
        taskCfg['backbones'][0][3]['monitoring_area'] = parking_mask
        taskCfg['backbones'][0][3]['is_process'] = True
        # 此段代码用于绘制图像进行检查
        # ------------------------
        draw_mask(mmcv.VideoReader(filepath)[10],'park_cover.jpg',all_point_array)
        # ------------------------
    if 'lane_monitoring_area' in cfg_data.keys():
        if 'lane_no_allow_cars' not in cfg_data.keys():
            raise RuntimeError('如果已经提供车道检测区域，请也提供禁止出现车辆信息')
        taskCfg['backbones'][0][4]['is_process'] = True
        lane_no_allow_cars = cfg_data['lane_no_allow_cars']
        all_point_array = [np.array(x, dtype=np.int32) for x in cfg_data['lane_monitoring_area']]
        mask = np.ones_like(mmcv.VideoReader(filepath)[10][:,:,0])
        for lane_area, no_allow_flag in zip(all_point_array, lane_no_allow_cars.keys()):
            new_mask = cv2.fillPoly(mask, [lane_area],int(no_allow_flag))
        taskCfg['backbones'][0][4]['monitoring_area'] = new_mask
        taskCfg['backbones'][0][4]['no_allow_car'] = lane_no_allow_cars
        # 此段代码用于绘制图像进行检查
        # ------------------------
        draw_mask(mmcv.VideoReader(filepath)[10],'lane_cover.jpg',all_point_array)
        # ------------------------
    if 'person_monitoring_area' in cfg_data.keys():
        all_point_array = [np.array(x, dtype=np.int32) for x in cfg_data['person_monitoring_area']]
        mask = np.ones_like(mmcv.VideoReader(filepath)[10][:,:,0])
        new_mask = cv2.fillPoly(mask, all_point_array, 1)
        taskCfg['backbones'][0][5]['monitoring_area'] = new_mask
        taskCfg['backbones'][0][5]['is_process'] = True
        # 此段代码用于绘制图像进行检查
        # ------------------------
        draw_mask(mmcv.VideoReader(filepath)[10],'person_cover.jpg',all_point_array)
        # ------------------------
    return taskCfg