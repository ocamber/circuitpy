import storage
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = "TRINKEY"
