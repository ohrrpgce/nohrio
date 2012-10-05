def loadsaveok(cls, source, *args, **kwargs):
    """Construct cls from source file, save instance -> temp file,
       return if they're equal."""
    from tempfile import mktemp
    tmp = mktemp('nohrio')
    instance = cls(source=source, *args, **kwargs)
    instance.save(tmp)
    retval = (call(['diff', source, tmp]) == 0)