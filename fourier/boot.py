import storage
storage.remount("/")
m = storage.getmount("/")
m.label = "FOURIER_LF"
