import storage
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = "FOURIER_R2"
storage.remount("/", readonly=True)
storage.enable_usb_drive()
