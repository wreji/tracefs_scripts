import helpers.controls as controls

kmem_path = "/sys/kernel/tracing/events/kmem/"
kmalloc_path = "/sys/kernel/tracing/events/kmem/kmalloc/"
kfree_path = "/sys/kernel/tracing/events/kmem/kfree/"
kmem_cache_alloc_path = "/sys/kernel/tracing/events/kmem/kmem_cache_alloc/"
kmem_cache_free_path = "/sys/kernel/tracing/events/kmem/kmem_cache_free/"

def activate_kmem_kmalloc():
    controls.write_control_string(kmalloc_path + "enable", "1")    

def deactivate_kmem_kmalloc():
    controls.write_control_string(kmalloc_path + "enable", "0")    

def activate_kmem_kfree():
    controls.write_control_string(kfree_path + "enable", "1")    

def deactivate_kmem_kfree():
    controls.write_control_string(kfree_path + "enable", "0")    

def activate_kmem_cache_alloc():
    controls.write_control_string(kmem_cache_alloc_path + "enable", "1")    

def deactivate_kmem_cache_alloc():
    controls.write_control_string(kmem_cache_alloc_path + "enable", "0")    

def activate_kmem_cache_free():
    controls.write_control_string(kmem_cache_free_path + "enable", "1")    

def deactivate_kmem_cache_free():
    controls.write_control_string(kmem_cache_free_path + "enable", "0")    

def set_kmem_kalloc_filter(filter: str):
    controls.write_control_string(kmalloc_path + "filter", filter)    

def clr_kmem_kmalloc_filter():
    set_kmem_kalloc_filter("")

def set_kmem_kfree_filter(filter: str):
    controls.write_control_string(kfree_path + "filter", filter)

def clr_kmem_kfree_filter():
    set_kmem_kfree_filter("")    

def set_kmem_cache_alloc_filter(filter: str):
    controls.write_control_string(kmem_cache_alloc_path + "filter", filter)

def clr_kmem_cache_alloc_filter():
    set_kmem_cache_alloc_filter("")

def set_kmem_cache_free_filter(filter: str):
    controls.write_control_string(kmem_cache_free_path + "filter", filter)

def clr_kmem_kfree_filter():
    set_kmem_cache_free_filter("")

def set_kmem_filter(filter: str):
    controls.write_control_string(kmem_path + "filter", filter)

def clr_kmem_filter():
    set_kmem_filter("")