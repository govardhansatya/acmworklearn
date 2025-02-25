from ultralytics import YOLO

# Initialize the model with a pretrained weight file
model = YOLO("yolov8n.pt")

# Tune the model by passing valid keyword arguments.
# Note: Only pass arguments that are recognized by the YOLO CLI.
model.tune(
    data="coco8.yaml",   # path to your dataset config file
    epochs=30,           # total training epochs
    iterations=90,      # number of iterations for tuning
    imgsz=640,           # image size for training
    optimizer="auto",    # choose the optimizer ("auto", "AdamW", "SGD", etc.)
    cos_lr=False,        # whether to use a cosine learning rate schedule
    lr0=0.01,            # initial learning rate
    lrf=0.01,            # final learning rate factor
    momentum=0.937,      # momentum value
    weight_decay=0.0005, # weight decay (regularization)
    dropout=0.0,         # dropout rate (disable if using weight_decay)
    
    # Warmup parameters
    warmup_epochs=3.0,
    warmup_momentum=0.8,
    warmup_bias_lr=0.1,
    
    # Label smoothing
    label_smoothing=0.0,
    
    # Data augmentation settings
    hsv_h=0.015,         # hue augmentation
    hsv_s=0.7,           # saturation augmentation
    hsv_v=0.4,           # brightness augmentation
    degrees=0.0,         # rotation augmentation
    translate=0.1,       # translation augmentation
    scale=0.5,           # scaling augmentation
    shear=0.0,           # shear augmentation
    perspective=0.0,     # perspective augmentation
    flipud=0.0,          # vertical flip probability
    fliplr=0.0,          # horizontal flip probability
    bgr=0.0,             # channel reordering (if necessary)
    mosaic=1.0,          # mosaic augmentation probability
    mixup=0.0,           # mixup augmentation probability
    copy_paste=0.0,      # copy-paste augmentation probability
    erasing=0.4,         # random erasing augmentation probability
    crop_fraction=1.0,   # fraction of the image to crop
    
    # Loss settings for object detection
    box=7.5,             # weight for bounding box loss
    cls=0.5,             # weight for classification loss
    dfl=1.5,             # weight for distribution focal loss
    
    # Miscellaneous settings
    pretrained=True,     # use pretrained weights
    single_cls=False,    # single-class training flag
    rect=False,          # rectangular training images flag
    close_mosaic=10,     # disable mosaic augmentation for the last 10 epochs
    fraction=1.0,        # fraction of the dataset to use
    freeze=None          # number of layers to freeze
)
