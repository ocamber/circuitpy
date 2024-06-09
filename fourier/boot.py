import storage
#storage.remount("/", readonly=True)
m = storage.getmount("/")
m.label = "FOURIER_LF"
