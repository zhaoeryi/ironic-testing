#!/usr/local/bin/python

#===============================================================================
# define error code here... Todo: populate error code with real error condition
#===============================================================================
FM_CIM_EC_0 = 0
FM_CIM_EC_1 = 1
FM_CIM_EC_2 = 2
FM_CIM_EC_3 = 3
FM_CIM_EC_4 = 4

#===============================================================================
# define function here
#===============================================================================

class fw_error(Exception): 
    '''
    arg1: error code
    arg2: error message 
    '''

    
import sys
from pywbem import *
from msg_decorator import *   # will be obsolete



class cim_proxy():
    def __init__(self, ip, userid, password):
        self.ip = ip
        self.userid = userid
        self.password = password
        self.conn = WBEMConnection('http://%s:5988' % ip, (userid, password), default_namespace=u'root/cimv2')    
        
    def request_power_state_change(self, activity):

        str_svc_name = 'CIM_PowerManagementService'
        #print 'Get Instance Name of ', str_svc_name, '...'
        try:
            names = self.conn.EnumerateInstanceNames(str_svc_name)[0]
        except CIMError, arg:
            raise Exception('Failed to Enumerate Instance %s on %s'% (str_svc_name, ip))
            
        instance_name = 'IBM_ComputerSystem'
        #print 'Get Instance Name of ', str_svc_name, '...'
        try:
            ref_ComputerSystem = self.conn.EnumerateInstanceNames(instance_name)[0]
        except CIMError, arg:
            raise Exception('Failed to Enumerate Instance %s' % instance_name)
            
        
        inparams = {'PowerState':Uint16(activity)}
        inparams['ManagedElement'] = ref_ComputerSystem
        
        # test code: get build id...
        # print get_build_id('imm_primary', conn)
        # Launch FW update job
        #logging.info( 'Setting host power to %d...' % activity)
        
        try:
            #(retcode, outparam) = call_func_dict("conn.InvokeMethod", inparams, 'InstallFromURI', str(names[0])) 
            #conn.InvokeMethod(methodname='InstallFromURI', localobject=names[0], params=inparams)
            (retcode, outparam) = self.conn.InvokeMethod('RequestPowerStateChange',\
                              names, \
                              **inparams)
        except CIMError, arg: 
            #print( 'fail with error message: ', arg[0], arg[1])
            raise Exception('Cannot execute %s' % "RequestPowerStateChange")
         
        if retcode != Uint32(0):
            raise Exception('Return code (%s - %s) of RequestPowerStateChange indicate operation wasn\'t\
                                        successful' % (str(retcode), 
                                                       str(outparam)
                                                       )
                           )
            
    
    
    
    #===============================================================================
    # Below API(s) are not object oriented, 
    # and will be eventually abandoned and 
    # transit to object based methods provided in cim_proxy class 
    #===============================================================================
            

def wait_for(func, exp_ret, timeout, *param):
    '''
    This function will execute synchronized wait on function "func"
    until the return of "func" matches "exp_ret".
    *param is the list of parameters that func takes. dict is not supported
    Timeout is give by seconds.
    Interval is hardcoded by 2 seconds 
    
    return: 0 on success, -1 on failure
    '''
    if timeout <= 0:
        raise Exception, 'invalid parameter for timeout: ' + timeout
    
    interval = 2
    import time
    
    # acquire timestamp at begin
    begin_ts = time.time()
    while int(time.time()-begin_ts) < timeout :
        rc = func(*param)
        if rc == exp_ret:
            # match, exit
            return 0, rc
        else:
            m.info('...') 
            time.sleep(interval)

    # if we are here, we never succeed
    return -1, rc

def wait_not_for(func, exp_ret, timeout, *param):
    '''
    This function will execute synchronized wait on function "func"
    until the return of "func" does NOT match "exp_ret".
    *param is the list of parameters that func takes. dict is not supported
    Timeout is give by seconds.
    Interval is hardcoded by 2 seconds 
    
    return: 0 on success, -1 on failure
    '''
    if timeout <= 0:
        raise Exception, 'invalid parameter for timeout: ' + timeout
    
    interval = 2
    import time
    
    # acquire timestamp at begin
    begin_ts = time.time()
    while int(time.time()-begin_ts) < timeout :
        rc = func(*param)
        if rc != exp_ret:
            # match, exit
            return 0, rc
        else:
            m.info('...')
            time.sleep(interval)

    # if we are here, we never succeed
    return -1, rc



def reset_imm(cim_conn):
    '''
    Calling this function will reset IMM
    return 0 on success which is defined by the return of cim command
    '''

    str_svc_name = 'IBM_ManagementController'
    #print 'Get Instance Name of ', str_svc_name, '...'
    try:
        names = cim_conn.EnumerateInstanceNames(str_svc_name)[0]
    except CIMError, arg:
        m.info( arg[0], arg[1])
        return -1

    #test code
    (retcode, outparam) = cim_conn.InvokeMethod('RequestStateChange', 
                                            names,
                                            RequestedState=Uint16(11)
                                            )    
    
    return retcode
     

def get_build_id(fw_type, cim_conn):
    '''
    return build ID if succeed
    return None if fail
    '''
    fw_support_list = {'imm_primary':'swid1', 
                       'imm_backup':'swid2', 
                       'uefi_primary':'swid3', 
                       'uefi_backup':'swid4',
                       'dsa':'swid5'}
    
    if fw_type not in fw_support_list.keys():
        raise fw_error(FM_CIM_EC_0, "Unsupported fw type '%s' provided. Supported fw types are: %s" % (fw_type, fw_support_list.keys())) 
    
    # send get instance command: CIM_SoftwareIdentity.InstanceID="CIM:swid5"
    sid_inst = CIMInstanceName(classname='CIM_SoftwareIdentity',
                                     keybindings=NocaseDict({'InstanceID' : 'CIM:'+fw_support_list[fw_type]}),
                                     namespace=u'root/cimv2')
    try:
        fw_state = cim_conn.GetInstance(sid_inst)
    except Exception, e:
        #print 'fail to get SW id %s with error message "%s"' % (fw_type, e.message)
        return None
    
    if not 'VersionString' in fw_state.keys():
        m.info( "%s not in return FW state" % 'VersionString')
        return None 
    
    return fw_state['VersionString']


def cim_update(ip, fw_type, sftp_url, userid='USERID',password='PASSW0RD', log_prefix='uxspi_sim'):
    fw_support_list = {'imm_primary':'swid1', 
                       'imm_backup':'swid2', 
                       'uefi_primary':'swid3', 
                       'uefi_backup':'swid4',
                       'dsa':'swid5'}
    
    if fw_type not in fw_support_list.keys():
        raise fw_error(FM_CIM_EC_0, "Unsupported fw type '%s' provided. Supported fw types are: %s" % (fw_type, fw_support_list.keys())) 
    
    

    global m
    m = msg_decorator(log_prefix)     
    m.info('Update Job Info:')
    m.info('IMM IP:', ip)
    m.info('Firmware Type:', fw_type)
    m.info('Remote URL:', sftp_url)
    conn = WBEMConnection('http://%s:5988'%ip, (userid, password), default_namespace=u'root/cimv2')  
    
    str_svc_name = 'CIM_SoftwareInstallationService'
    #print 'Get Instance Name of ', str_svc_name, '...'
    try:
        names = conn.EnumerateInstanceNames(str_svc_name)[0]
    except Exception, arg:
        #m.info( arg[0], arg[1])
        raise fw_error(FM_CIM_EC_1, 'Cannot Send CIM CMD for %s class to host %s. CIM msg is: %s' % (str_svc_name, ip, arg.message))
     
    # Get existing build id
    try:
        build_id = get_build_id(fw_type, conn)
    except fw_error:
        pass
    
    if build_id == None:
        m.info('Failed to get build ID, continue anyway')
    else:
        m.info('Current BUILD of of %s is: %s' % (fw_type, build_id.split('-', 1)[0]))
    
    # Retrieve SW ID for FW
    inparams = {'URI':sftp_url, 
            #'Target':u'/root/cimv2:CIM_SoftwareIdentity.InstanceID="CIM:swid1"', 
            'InstallOptions':[Uint16(4)],
            'InstallOptionsValues':''}
    
    
    
    inparams['Target'] = CIMInstanceName(classname='CIM_SoftwareIdentity', 
                                         keybindings=NocaseDict({'InstanceID' : 'CIM:'+fw_support_list[fw_type]}), 
                                         namespace=u'root/cimv2')
    
    # test code: get build id...
    # print get_build_id('imm_primary', conn)
    # Launch FW update job
    m.info( 'launch update job...')
    
    try:
        #(retcode, outparam) = call_func_dict("conn.InvokeMethod", inparams, 'InstallFromURI', str(names[0])) 
        #conn.InvokeMethod(methodname='InstallFromURI', localobject=names[0], params=inparams)
        (retcode, outparam) = conn.InvokeMethod('InstallFromURI',\
                          names, \
                          **inparams)
    except CIMError, arg: 
        m.info( 'fail with error message: ', arg[0], arg[1])
        raise fw_error(FM_CIM_EC_1, 'Cannot reach IMM on %s via CIM channel.' % ip)
    
#    print 'return code is:', retcode
#    print 'type of param is:', type(outparam)
#    print 'param content:'outparam
#    print type(retcode)
    if not retcode == Uint32(4096):
        raise fw_error(FM_CIM_EC_1, 'Error, CIM return code is ""' % retcode)
        
        

    m.info( 'job launch successful, job ID is:',outparam['Job']['InstanceID']) 
    
    flash_job_inst = CIMInstanceName(classname='CIM_ConcreteJob',
                                     keybindings=NocaseDict({'InstanceID' : outparam['Job']['InstanceID']}),
                                     namespace=u'root/cimv2')
    
    while True:
        # retry for possible CIM connection failure
        retry_cnt = 30
        while retry_cnt > 0:
            try:
                job_state = conn.GetInstance(flash_job_inst)
                break
            except:
                m.info( 'fail to get Instance of %s, retry...' % flash_job_inst)
                retry_cnt -= 1
                time.sleep(1)
        
        if retry_cnt == 0:        
            flash_success = False
            raise fw_error(FM_CIM_EC_0, "Lost connection with IMM when polling for job state (sending get instance cmd)")
                
        
        
        if job_state['JobState'] == Uint16(4):
            m.info( 'Job running with Status Code', job_state['JobState'], '...')
            
            # Display OperationalStatus, StatusDescriptions, JobStatus 
            m.info('OperationalStatus = 0x%x' % int(job_state['OperationalStatus'][0]))
            m.info('JobStatus =', job_state['JobStatus'])
            m.info('StatusDescriptions =', job_state['StatusDescriptions'])
            import time
            time.sleep(5)   # interval is 5 seconds            

        elif job_state['JobState'] == Uint16(10):
            # important!! Must get detailed fail reson here. 
            m.info( "Job terminated with Exception", job_state['JobState'])
            # Display OperationalStatus, StatusDescriptions, JobStatus 
            m.info('OperationalStatus = 0x%x' % int(job_state['OperationalStatus'][0]))
            m.info('JobStatus =', job_state['JobStatus'])
            m.info('StatusDescriptions =', job_state['StatusDescriptions'])
            flash_success = False
            break         
        elif job_state['JobState'] == Uint16(7):
            m.info( 'Job finished succesfully with State code: ', job_state['JobState'])
            flash_success = True
            break
        else:
            m.info( "unsupported Job State Code:", job_state['JobState'])
            flash_success = False
            break
    
    if flash_success is False:
        raise fw_error(FM_CIM_EC_0, "Job terminated with Exception %s"% job_state['JobState'])
        
    # IMM need to perform reboot and check if new image is applied
    # Perform reboot: 
    if fw_type != 'imm_primary':
        return 0;
    
    
    m.info('Reset IMM to activate new Firmware...')
    if reset_imm(conn) != 0:
        raise fw_error(FM_CIM_EC_0, 'fail to activate IMM')
    # wait IMM to lost connection, Timeout is 2 minutes
    m.info( "waiting for IMM to lose connection...")
    import os
    (rc, func_rc) = wait_for((lambda x: os.system('ping -c 2 %s 2>&1 > /dev/null' % x)), 
             256, 
             120, 
             ip)
    
    if rc != 0:
        raise fw_error(FM_CIM_EC_0, 'IMM failed to reboot, abort')
    else:
        m.info('Done')
        
        
    # wait IMM to come back using ping command. Timeout is 9 minutes
    m.info( 'Waiting for IMM to come back')
    (rc, func_rc) = wait_for((lambda x: os.system('ping -c 2 %s 2>&1 > /dev/null' % x)), 
             0, 
             60*9, 
             ip)
    
    if rc != 0:
        m.error( "IMM did not came back in %s seconds, aborted" % str(60*9))
    else:
        m.info( 'Done')    
        
    # once IMM come back, send CIM command to retrieve new BUILD ID. Timeout is 3 minutes
    m.info('Waiting to get BUILD ID from IMM')
    (rc, func_rc) = wait_not_for(get_build_id, 
             None, 
             60*3, 
             'imm_primary', conn)
    
    if rc != 0:
        m.error( "Cannot get build ID via CIM command in %s seconds" % (60*3))
    else:
        m.info( 'Done')
        
    m.info( "new IMM build ID is: %s" % func_rc.split('-', 1)[0])    
    
    return 0

def collect_ffdc(ip, sftp_url, userid, password, log_prefix='cim_update_core'):
    '''
    Collect IMM FFDC on specified IP through CIM interface
    '''
    
    m = msg_decorator(log_prefix)     
    
    # find sftp credential if any
    #print sftp_url.find('@')#debug

    if sftp_url.find('@') != -1:
        cred = sftp_url.split('@', 1)[0]
        export_url = sftp_url.split('@', 1)[1]
        
        #print cred#debug
        if cred.find(':') == -1:
            m.error('externel FTP/SFTP require format: USER:PWD@URL')
            sys.exit(-1)
        sftp_username = cred.split(':', 1)[0]
        sftp_password = cred.split(':', 1)[1]
    else:
        #print 'no cred'#debug
        export_url = sftp_url
        sftp_username = ''
        sftp_password = ''
    
    m.info('SFTP URL:', export_url)
    m.info('SFTP User:', sftp_username)
    m.info('SFTP PWD: ********')
    
    cim_conn = WBEMConnection('http://%s:5988'%ip, (userid, password), default_namespace=u'root/cimv2')    
    
    str_svc_name = 'IBM_FFDCService'
    #print 'Get Instance Name of ', str_svc_name, '...'
    try:
        names = cim_conn.EnumerateInstanceNames(str_svc_name)[0]
    except CIMError, arg:
        m.info( 'CIMError:', arg[0], arg[1])
        #raise fw_error(FM_CIM_EC_4, 'FFDC exception - Failed to send CIM cmd to %s'%ip)
        return -1

    

    inparams = {'InitializationNeeded':True,
            'ExportURI':export_url, 
            'Username':sftp_username, 
            'Password':sftp_password}
    
    
    
    inparams['DataCollectionType'] = CIMInstanceName(classname='IBM_FFDCData', 
                                         keybindings=NocaseDict({'InstanceID' : 'FFDCdata1'}), 
                                         namespace=u'root/cimv2')
    
    # test code: get build id...
    # print get_build_id('imm_primary', conn)
    # Launch FW update job
    m.info( 'Gathering FFDC, this may take few minutes...')
    
    try:
        #(retcode, outparam) = call_func_dict("conn.InvokeMethod", inparams, 'InstallFromURI', str(names[0])) 
        #conn.InvokeMethod(methodname='InstallFromURI', localobject=names[0], params=inparams)
        (retcode, outparam) = cim_conn.InvokeMethod('ExportData',\
                          names, \
                          **inparams)
    except CIMError, arg: 
        m.info( 'fail with error message: ', arg[0], arg[1])
        return -1    
    
    m.info('FFDC finished with return code %d' % int(retcode))
    
    return int(retcode) 
    
    
if __name__ == '__main__':
    import sys
    
    toy = cim_proxy("192.168.5.200", "USERID", "PASSW0RD")
    toy.request_power_state_change(int(sys.argv[1]))
    