from cfg import TaskConfig
CrossRoadsTaskFakeCfg = {
    'head': [
        {
            'type': 'EquivalentHead',
            'filename': 'videoData/video/gta5_small.mp4',
            'json_filename': 'videoData/json/gta5_small.json',
            'step': TaskConfig.BATCH_SIZE,
            'cache_capacity': 100,
            'haveImg': True
        }
    ],
    'tracker': [
        {
            'type': 'SORT_Track'
        }
    ],
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
                'no_allow_car':{}, # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
                'is_process':False # 是否开启该组件
            },
            # # 数据库写入组件
            # {
            #     'type': 'InformationCollectorComponent',
            #     'host': Cfg.host,
            #     'user': Cfg.user,
            #     'password': Cfg.password,
            #     'db': Cfg.database,
            #     'img_save_path':Cfg.img_save_dir
            # },

            # {
            #   'type': 'DrawBoundingBoxComponent'  # 画框框
            # },
            # {
            #     'type': 'RtmpWriteComponent',
            #     'resolution': (1920, 1080),
            #     'fps': 30,
            #     'rtmpUrl': TaskConfig.RTMP_URL
            # }

        ]
    ]
}
