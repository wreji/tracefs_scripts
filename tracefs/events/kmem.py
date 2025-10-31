kmalloc_path = "/sys/kernel/tracing/events/kmem/kmalloc/"
kfree_path = "/sys/kernel/tracing/events/kmem/kfree/"
kmem_cache_alloc_path = "/sys/kernel/tracing/events/kmem/kmem_cache_alloc/"
kmem_cache_free_path = "/sys/kernel/tracing/events/kmem/kmem_cache_free/"

def activate_kmem_kmalloc():
    with open(kmalloc_path+"enable", "w", encoding="utf-8") as f:
        f.write("1")

def deactivate_kmem_kmalloc():
    with open(kmalloc_path+"enable", "w", encoding="utf-8") as f:
        f.write("0")

def activate_kmem_kfree():
    with open(kfree_path + "enable", "w", encoding="utf-8") as f:
        f.write("1")

def deactivate_kmem_kfree():
    with open(kfree_path + "enable", "w", encoding="utf-8") as f:
        f.write("0")

def activate_kmem_cache_alloc():
    with open(kmem_cache_alloc_path + "enable", "w", encoding="utf-8") as f:
        f.write("1")

def deactivate_kmem_cache_alloc():
    with open(kmem_cache_alloc_path + "enable", "w", encoding="utf-8") as f:
        f.write("0")

def activate_kmem_cache_free():
    with open(kmem_cache_free_path + "enable", "w", encoding="utf-8") as f:
        f.write("1")

def deactivate_kmem_cache_free():
    with open(kmem_cache_free_path + "enable", "w", encoding="utf-8") as f:
        f.write("0")