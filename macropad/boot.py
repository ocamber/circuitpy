import storage
import supervisor
supervisor.set_next_stack_limit(4096 + 4096)
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = "MACROPAD"

