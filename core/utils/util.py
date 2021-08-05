def errRun( *cmd, **kwargs ):
    """
    Run a command and return stdout, stderr and return code
    cmd: string or list of command and args
    stderr: STDOUT to merge stderr with stdout
    shell: run command using shell
    echo: monitor output to console
    """
    # By default we separate stderr, don't run in a shell, and don't echo
    stderr = kwargs.get( 'stderr', PIPE )
    shell = kwargs.get( 'shell', False )
    echo = kwargs.get( 'echo', False )
    if echo:
        # cmd goes to stderr, output goes to stdout
        info( cmd, '\n' )
    if len( cmd ) == 1:
        cmd = cmd[ 0 ]
    # Allow passing in a list or a string
    if isinstance( cmd, BaseString ) and not shell:
        cmd = cmd.split( ' ' )
        cmd = [ str( arg ) for arg in cmd ]
    elif isinstance( cmd, list ) and shell:
        cmd = " ".join( arg for arg in cmd )
    debug( '*** errRun:', cmd, '\n' )
    popen = Popen( cmd, stdout=PIPE, stderr=stderr, shell=shell )
    # We use poll() because select() doesn't work with large fd numbers,
    # and thus communicate() doesn't work either
    out, err = '', ''
    poller = poll()
    poller.register( popen.stdout, POLLIN )
    fdtofile = { popen.stdout.fileno(): popen.stdout }
    outDone, errDone = False, True
    if popen.stderr:
        fdtofile[ popen.stderr.fileno() ] = popen.stderr
        poller.register( popen.stderr, POLLIN )
        errDone = False
    while not outDone or not errDone:
        readable = poller.poll()
        for fd, event in readable:
            f = fdtofile[ fd ]
            if event & POLLIN:
                data = f.read( 1024 )
                if Python3:
                    data = data.decode( Encoding )
                if echo:
                    output( data )
                if f == popen.stdout:
                    out += data
                    if data == '':
                        outDone = True
                elif f == popen.stderr:
                    err += data
                    if data == '':
                        errDone = True
            else:  # POLLHUP or something unexpected
                if f == popen.stdout:
                    outDone = True
                elif f == popen.stderr:
                    errDone = True
                poller.unregister( fd )

    returncode = popen.wait()
    # Python 3 complains if we don't explicitly close these
    popen.stdout.close()
    if stderr == PIPE:
        popen.stderr.close()
    debug( out, err, returncode )
    return out, err, returncode


def quietRun(cmd, **kwargs):
    """
    Run a command and return merged stdout and stderr
    :param cmd:
    :param kwargs:
    :return:
    """
    return errRun(cmd, stderr=STDOUT, **kwargs)[0]
