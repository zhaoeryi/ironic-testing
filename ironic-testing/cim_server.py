#!/usr/bin/python
import os, re, json, sys
import string
from tests import base
import pprint
from pywbem import *

CONST_ENABLED = 2
CONST_KB = 1024
CONST_FDIMM = 11;

const_power_state_dict = {
            1:"Other",
            2: "On",
            3: "Sleep - Light",
            4: "Sleep -Deep",
            5: "Power Cycle (Off - Soft)",
            6: "Off - Hard",
            7: "Hibernate (Off - Soft)",
            8: "Off - Soft",
            9: "Power Cycle (Off-Hard)",
            10: "Master Bus Reset",
            11: "Diagnostic Interrupt (NMI)",
            12: "Off - Soft Graceful",
            13: "Off - Hard Graceful",
            14: "Master Bus Reset Graceful",
            15: "Power Cycle (Off - Soft Graceful)",
            16: "Power Cycle (Off - Hard Graceful)",
            17: "Diagnostic Interrupt (INIT)"
}

const_processor_family_dict = {
        1:"OTHER",
        2:"UNKNOWN",
        3:"The_8086",
        4:"The_80286",
        5:"The_80386",
        6:"The_80486",
        7:"The_8087",
        8:"The_80287",
        9:"The_80387",
        10:"The_80487",
        11:"PENTIUMA_R_BRAND",
        12:"PENTIUMA_R_PRO",
        13:"PENTIUMA_R_II",
        14:"PENTIUMA_R_PROCESSOR_WITH_MMXAMAP_PUT_TM_TECHNOLOGY",
        15:"CELERONA_TM",
        16:"PENTIUMA_R_II_XEONAMAP_PUT_TM",
        17:"PENTIUMA_R_III",
        18:"M1_FAMILY",
        19:"M2_FAMILY",
        20:"INTEL_R_CELERON_R_M_PROCESSOR",
        21:"INTEL_R_PENTIUM_R_4_HT_PROCESSOR",
        24:"K5_FAMILY",
        25:"K6_FAMILY",
        26:"K6_2",
        27:"K6_3",
        28:"AMD_ATHLON_TM_PROCESSOR_FAMILY",
        29:"AMD_R_DURON_TM_PROCESSOR",
        30:"AMD29000_FAMILY",
        31:"K6_2PLUS",
        32:"POWER_PC_FAMILY",
        33:"POWER_PC_601",
        34:"POWER_PC_603",
        35:"POWER_PC_603Plus",
        36:"POWER_PC_604",
        37:"POWER_PC_620",
        38:"POWER_PC_X704",
        39:"POWER_PC_750",
        40:"INTEL_R_CORE_TM_DUO_PROCESSOR",
        41:"INTEL_R_CORE_TM_DUO_MOBILE_PROCESSOR",
        42:"INTEL_R_CORE_TM_SOLO_MOBILE_PROCESSOR",
        43:"INTEL_R_ATOM_TM_PROCESSOR",
        48:"ALPHA_FAMILY",
        49:"ALPHA_21064",
        50:"ALPHA_21066",
        51:"ALPHA_21164",
        52:"ALPHA_21164PC",
        53:"ALPHA_21164A",
        54:"ALPHA_21264",
        55:"ALPHA_21364",
        56:"AMD_TURION_TM_II_ULTRA_DUAL_CORE_MOBILE_M_PROCESSOR_FAMILY",
        57:"AMD_TURION_TM_II_DUAL_CORE_MOBILE_M_PROCESSOR_FAMILY",
        58:"AMD_ATHLON_TM_II_DUAL_CORE_MOBILE_M_PROCESSOR_FAMILY",
        59:"AMD_OPTERON_TM_6100_SERIES_PROCESSOR",
        60:"AMD_OPTERON_TM_4100_SERIES_PROCESSOR",
        64:"MIPS_FAMILY",
        65:"MIPS_R4000",
        66:"MIPS_R4200",
        67:"MIPS_R4400",
        68:"MIPS_R4600",
        69:"MIPS_R10000",
        80:"SPARC_FAMILY",
        81:"SUPERSPARC",
        82:"MICROSPARC_II",
        83:"MICROSPARC_IIEP",
        84:"ULTRASPARC",
        85:"ULTRASPARC_II",
        86:"ULTRASPARC_IIi",
        87:"ULTRASPARC_III",
        88:"ULTRASPARC_IIIi",
        96:"The_68040",
        97:"FAMILY_68XXX",
        98:"The_68000",
        99:"The_68010",
        100:"The_68020",
        101:"The_68030",
        112:"HOBBIT_FAMILY",
        120:"CRUSOE_TM_TM5000_FAMILY",
        121:"CRUSOE_TM_TM3000_FAMILY",
        122:"EFFICEON_TM_TM8000_FAMILY",
        128:"WEITEK",
        130:"ITANIUM_TM_PROCESSOR",
        131:"AMD_ATHLON_TM_64_PROCESSOR_FAMILY",
        132:"AMD_OPTERON_TM_PROCESSOR_FAMILY",
        133:"AMD_SEMPRON_TM_PROCESSOR_FAMILY",
        134:"AMD_TURION_TM_64_MOBILE_TECHNOLOGY",
        135:"DUAL_CORE_AMD_OPTERON_TM_PROCESSOR_FAMILY",
        136:"AMD_ATHLON_TM_64_X2_DUAL_CORE_PROCESSOR_FAMILY",
        137:"AMD_TURION_TM_64_X2_MOBILE_TECHNOLOGY",
        138:"QUAD_CORE_AMD_OPTERON_TM_PROCESSOR_FAMILY",
        139:"THIRD_GENERATION_AMD_OPTERON_TM_PROCESSOR_FAMILY",
        140:"AMD_PHENOM_TM_FX_QUAD_CORE_PROCESSOR_FAMILY",
        141:"AMD_PHENOM_TM_X4_QUAD_CORE_PROCESSOR_F",
        142:"AMD_PHENOM_TM_X2_DUAL_CORE_PROCESSOR_FAMILY",
        143:"AMD_ATHLON_TM_X2_DUAL_CORE_PROCESSOR_FAMILY",
        144:"PA_RISC_FAMILY",
        145:"PA_RISC_8500",
        146:"PA_RISC_8000",
        147:"PA_RISC_7300LC",
        148:"PA_RISC_7200",
        149:"PA_RISC_7100LC",
        150:"PA_RISC_7100",
        160:"V30_FAMILY",
        161:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_3200_SERIES",
        162:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_3000_SERIES",
        163:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_5300_SERIES",
        164:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_5100_SERIES",
        165:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_5000_SERIES",
        166:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_LV",
        167:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_ULV",
        168:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_7100_SERIES",
        169:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_5400_SERIES",
        170:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR",
        171:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_5200_SERIES",
        172:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_7200_SERIES",
        173:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_7300_SERIES",
        174:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_7400_SERIES",
        175:"MULTI_CORE_INTEL_R_XEON_R_PROCESSOR_7400_SERIES",
        176:"PENTIUM_R_III_XEON_TM",
        177:"PENTIUM_R_III_PROCESSOR_WITH_INTEL_R_SPEEDSTEP_TM_TECHNOLOGY",
        178:"PENTIUM_R_4",
        179:"INTEL_R_XEON_TM",
        180:"AS400_FAMILY",
        181:"INTEL_R_XEON_TM_PROCESSOR_MP",
        182:"AMD_ATHLON_TM_XP_FAMILY",
        183:"AMD_ATHLON_TM_MP_FAMILY",
        184:"INTEL_R_ITANIUM_R_2",
        185:"INTEL_R_PENTIUM_R_M_PROCESSOR",
        186:"INTEL_R_CELERON_R_D_PROCESSOR",
        187:"INTEL_R_PENTIUM_R_D_PROCESSOR",
        188:"INTEL_R_PENTIUM_R_PROCESSOR_EXTREME_EDITION",
        189:"INTEL_R_CORE_TM_SOLO_PROCESSOR",
        190:"K7",
        191:"INTEL_R_CORE_TM_2_DUO_PROCESSOR",
        192:"INTEL_R_CORE_TM_2_SOLO_PROCESSOR",
        193:"INTEL_R_CORE_TM_2_EXTREME_PROCESSOR",
        194:"INTEL_R_CORE_TM_2_QUAD_PROCESSOR",
        195:"INTEL_R_CORE_TM_2_EXTREME_MOBILE_PROCESSOR",
        196:"INTEL_R_CORE_TM_2_DUO_MOBILE_PROCESSOR",
        197:"INTEL_R_CORE_TM_2_SOLO_MOBILE_PROCESSOR",
        198:"INTEL_R_CORE_TM_I7_PROCESSOR",
        199:"DUAL_CORE_INTEL_R_CELERON_R_PROCESSOR",
        200:"S_390_AND_ZSERIES_FAMILY",
        201:"ESA_390_G4",
        202:"ESA_390_G5",
        203:"ESA_390_G6",
        204:"Z_ARCHITECTUR_BASE",
        205:"INTEL_R_CORE_TM_I5_PROCESSOR",
        206:"INTEL_R_CORE_TM_I3_PROCESSOR",
        210:"VIA_C7_TM_M_PROCESSOR_FAMILY",
        211:"VIA_C7_TM_D_PROCESSOR_FAMILY",
        212:"VIA_C7_TM_PROCESSOR_FAMILY",
        213:"VIA_EDEN_TM_PROCESSOR_FAMILY",
        214:"MULTI_CORE_INTEL_R_XEON_R_PROCESSOR",
        215:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_3XXX_SERIES",
        216:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_3XXX_SERIES",
        217:"VIA_NANO_TM_PROCESSOR_FAMILY",
        218:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_5XXX_SERIES",
        219:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_5XXX_SERIES",
        221:"DUAL_CORE_INTEL_R_XEON_R_PROCESSOR_7XXX_SERIES",
        222:"QUAD_CORE_INTEL_R_XEON_R_PROCESSOR_7XXX_SERIES",
        223:"MULTI_CORE_INTEL_R_XEON_R_PROCESSOR_7XXX_SERIES",
        224:"MULTI_CORE_INTEL_R_XEON_R_PROCESSOR_3400_SERIES",
        230:"EMBEDDED_AMD_OPTERON_TM_QUAD_CORE_PROCESSOR_FAMILY",
        231:"AMD_PHENOM_TM_TRIPLE_CORE_PROCESSOR_FAMILY",
        232:"AMD_TURION_TM_ULTRA_DUAL_CORE_MOBILE_PROCESSOR_FAMILY",
        233:"AMD_TURION_TM_DUAL_CORE_MOBILE_PROCESSOR_FAMILY",
        234:"AMD_ATHLON_TM_DUAL_CORE_PROCESSOR_FAMILY",
        235:"AMD_SEMPRON_TM_SI_PROCESSOR_FAMILY",
        236:"AMD_PHENOM_TM_II_PROCESSOR_FAMILY",
        237:"AMD_ATHLON_TM_II_PROCESSOR_FAMILY",
        238:"SIX_CORE_AMD_OPTERON_TM_PROCESSOR_FAMILY",
        239:"AMD_SEMPRON_TM_M_PROCESSOR_FAMILY",
        250:"I860",
        251:"I960",
        254:"RESERVED_SMBIOS_EXTENSION",
        255:"RESERVED_UN_INITIALIZED_FLASH_CONTENT__LO",
        260:"SH_3",
        261:"SH_4",
        280:"ARM",
        281:"STRONGARM",
        300:"The_6X86",
        301:"MEDIAGX",
        302:"MII",
        320:"WINCHIP",
        350:"DSP",
        500:"VIDEO_PROCESSOR",
        65534:"RESERVED_FOR_FUTURE_SPECIAL_PURPOSE_ASSIGNMENT",
        65535:"RESERVED_UN_INITIALIZED_FLASH_CONTENT"
}
    
    
const_fan_status_dict = {
        0:"Unknown",
        1:"Other",
        2:"OK",
        3:"Degraded",
        4:"Stressed",
        5:"Predictive Failure",
        6:"Error",
        7:"Non-Recoverable Error",
        8:"Starting",
        9:"Stopping",
        10:"Stopped",
        11:"In Service",
        12:"No Contact",
        13:"Lost Communication",
        14:"Aborted",
        15:"Dormant",
        16:"Supporting Entity in Error",
        17:"Completed",
        18:"Power Mode",
        19:"Relocating"
}
    
const_fan_healthstate_dict = {
        0:"Unknown",
        5:"Normal",
        10:"Warning",
        15:"Minor",
        20:"Major",
        25:"Critical",
        30:"NonRecoverable"
}

const_powersupply_status_dict = {
        0:"UNKNOWN",
        2:"Status.OK",
        3:"DEGRADED",
        6:"Status.ERROR"
}

const_powersupply_healthstate_dict = {
        0:"NA",
        5:"GOOD",
        10:"WARNING",
        15:"MINOR_FAILURE",
        20:"MAJOR_FAILURE",
        25:"CRITICAL",
        30:"NONRECOVERABLE"
}

class PhysicalPackage(object):
    model = None
    tag = None
    description = None
    element_name = None
    manufacturer = None
    part_number = None
    serial_number = None
    manufacture_date = None
    sku = None
    
    def __str__(self):
        return str(vars(self))
    
class ServerSystemInformation(object):
    machine_name = None
    machine_type_model = None
    serial_number = None
    uuid = None
    server_power = None
    server_state = None
    total_hours_powered_on = None
    restart_count = None
    ambient_temperature = None
    enclosure_identify_led = None
    check_log_led = None  
    manufacturer_id = None

class ProcessorInformation(object):
    fru_name = None  # CPU 1
    manufacturer = None  # Intel(R) Corporation
    speed = None  #  2.60 GHz
    part_id = None  # E406 0300 FFFB EBBF 0000 0000 0000 0000
    type = None  # CENTRAL
    family = None  # Intel Xeon
    cores = None  # 8
    threads = None  # 16
    l1_cache_size = None  # 64K
    l2_cache_size = None  # 256K
    l3_cache_size = None  # 20480K
    voltage = None  # 1.2 V
    external_clock = None  # 100 MHz
    max_data_width = None  # 64-bit Capable
    description = None
    serial_number = None
    part_number = None
    manufacturer = None
    product_version = None

class MemoryInformation(object):
    fru_name = None  # DIMM 1
    description = None  # DIMM 1
    part_number = None  # M393B2G70QH0-CMA
    fru_serial_number = None  # 15856C60
    manuf_date = None  # 1114
    type = None  # DDR3
    size = None  # 16 GB 

class FanInformation(object):
    fru_name = None  # Fan 1A Tach
    speed = None  # 5520
    max_speed = None
    status = None
    health_state = None

class PowerSupplyInformation(object):
    status = None  # Normal
    rated_power = None  # 550
    fru_name = None # Power Supply 1
    part_number = None
    fru_number = None  # 94Y8110
    serial_number = None
    manufacturer = None
    power_on_duration = None  # 6,958 hour(s)
    power_cycles = None  # 46
    errors = None  # 0    
    health_state = None
    
    
       
class ServerCimConnector(object):

    def __init__(self, url, userid, password, namespace):
        
        self.url = url
        self.userid = userid
        self.password = password
        self.namespace = namespace
        self.conn = WBEMConnection(self.url, creds=(self.userid, self.password), default_namespace=self.namespace, timeout=180)
        
    def _build_identifying_dict(self, obj):
        arr_identifying_descriptions = obj['IdentifyingDescriptions']
        arr_identifying_info = obj['OtherIdentifyingInfo']
        
        pairs = {}
        for i in range(len(arr_identifying_descriptions)):
            pairs[arr_identifying_descriptions[i]] = arr_identifying_info[i]
        return pairs
    
    def _get_system_chassis_instance(self, cmp):
        chs = self.conn.Associators (cmp.path, AssocClass='CIM_ComputerSystemPackage', ResultClass='IBM_Chassis', Role='Dependent', ResultRole='Antecedent')
        if (len(chs) == 0):
            raise Exception("No instances of System 'CIM_Chassis' found")

        if (len(chs) > 1):
            print ("Too many associated Chassis 'CIM_Chassis' found returning first")
                
        chassis = chs[0]
        
        return chassis
                 
    def _get_chassis_uuid(self, cmp):
        identifying_dict = self._build_identifying_dict(cmp)
        uuid = identifying_dict['CIM:GUID']
        
        return uuid
    
    def _get_computer_instance(self):
        cmp = None
        
        computers = self.conn.EnumerateInstances('IBM_ComputerSystem')
        if(len(computers) > 0):
            cmp = computers[0]
        
        return cmp
    
    def get_physical_package(self, object_name, result_class='CIM_PhysicalPackage'):
        result = None
        pkgs = self.conn.Associators(object_name, AssocClass='CIM_Realizes', ResultClass=result_class, Role='Dependent', ResultRole='Antecedent')
        if(len(pkgs) > 0):
            pkg = pkgs[0]
            
            result = PhysicalPackage()
            result.model = pkg['Model']
            result.tag = pkg['Tag']
            result.description = pkg['Description']
            result.element_name = pkg['ElementName']
            result.manufacturer = pkg['Manufacturer']
            result.part_number = pkg['PartNumber']
            result.serial_number = pkg['SerialNumber']
            result.manufacture_date = pkg['ManufactureDate']
            result.sku = pkg['SKU']    
                    
        return result   
    
    def load_system_information(self):

        # get computer system
        cmp = self._get_computer_instance()
        if cmp is None:
            raise Exception("No instances of 'IBM_ComputerSystem' found")
        
        # get chassis
        chs = self._get_system_chassis_instance(cmp)
        
        result = ServerSystemInformation()
        # mix up
        result.machine_type_model = chs['Model']
        result.serial_number = chs['SerialNumber']
        result.uuid = self._get_chassis_uuid(cmp)
        result.restart_count = cmp['NumberOfReboots']
        
        server_instances = self.conn.EnumerateInstances('CIM_ComputerSystem')
        if (len(server_instances) == 0):
            raise Exception("No instances of System 'CIM_ComputerSystem' found")
        for sr in server_instances:
            classname = sr['CreationClassName']
            if classname == 'IBM_ComputerSystem':
                pmInstances = self.conn.References(sr.path, ResultClass='CIM_AssociatedPowerManagementService', Role='UserOfService')
                if (len(pmInstances) == 0):
                    raise Exception("No References of CIM_AssociatedPowerManagementService found")
                
                for pm in pmInstances:
                    result.server_power = const_power_state_dict.get(pm['PowerState'])
                    
                sr_identifying_dict = self._build_identifying_dict(sr)
                if "CIM:ProductName" in sr_identifying_dict:
                    result.machine_name = sr_identifying_dict["CIM:ProductName"];     
                
            elif classname == 'IBM_ManagementController':
                enable_state = sr['EnabledState']
                if enable_state == CONST_ENABLED:
                    # it is enabled
                    sr_identifying_dict = self._build_identifying_dict(sr)
                    if 'Manufacturer ID-Product ID' in sr_identifying_dict:
                        result.manufacturer_id = sr_identifying_dict['Manufacturer ID-Product ID'];
                
        return result 


    def load_processor_information(self):
        procInstances = self.conn.EnumerateInstances('CIM_Processor')
        if (len(procInstances) == 0):
            raise Exception("No instances of System 'CIM_Processor' found")      
        
        result = []
        for pr in procInstances:
            enable_state = pr['EnabledState']
            if enable_state == CONST_ENABLED:
                rescs = ProcessorInformation()
                result.append(rescs)
                
                rescs.fru_name = pr['DeviceID']
                rescs.cores = pr['NumberOfEnabledCores']
                # Convert Mhz speed from CIM to GHz
                rescs.speed = pr['CurrentClockSpeed'] / 1000.0
                rescs.external_clock = pr['ExternalBusClockSpeed']
                
                rescs.description = pr['OtherFamilyDescription']
                if pr['Family'] in const_processor_family_dict:
                    rescs.family = const_processor_family_dict[pr['Family']];
                    
                chips = self.conn.Associators(pr.path, AssocClass='CIM_Realizes', ResultClass='CIM_Chip', Role='Dependent', ResultRole='Antecedent')
                for chip in chips:
                    rescs.part_number = chip['PartNumber']
                    rescs.serial_number = chip['SerialNumber']
                    rescs.manufacturer = chip['Manufacturer']
                    rescs.product_version = chip['Version']
                
                    cachemems = self.conn.Associators(chip.path, AssocClass="CIM_Realizes", ResultClass="CIM_CacheMemory", Role="Antecedent", ResultRole="Dependent")
                    for cachemem in cachemems:
                        deviceid = cachemem['DeviceID']
                        blocksize = cachemem['BlockSize']
                        numberofblocks = cachemem['NumberOfBlocks']
                        cachesize = 0L;
                        
                        # Calculate cache size in KB
                        if (blocksize == CONST_KB):
                            cachesize = numberofblocks
                        else:
                            cachesize = ((blocksize * numberofblocks) / CONST_KB)

                        if ("Cache Level 1" in deviceid):
                            rescs.l1_cache_size = cachesize

                        if ("Cache Level 2" in deviceid):
                            rescs.l2_cache_size = cachesize

                        if ("Cache Level 3" in deviceid):
                            rescs.l3_cache_size = cachesize
                    
        return result
 
    def load_memory_information(self):
        memInstances = self.conn.EnumerateInstances('CIM_PhysicalMemory');
        if (len(memInstances) == 0):
            raise Exception("No instances of System 'CIM_PhysicalMemory' found")      

        result = []
        for mem in memInstances :
            # MemoryType property should differentiate DIMM and FDIMM devices
            memType = mem['MemoryType']
            # Verify memory type if FlashDIMM then skip it
            if (memType == CONST_FDIMM):
                continue
            
            memInfo = MemoryInformation();
            result.append(memInfo)
            
            memInfo.fru_name = mem['Description']
            memInfo.description = mem['Description']
            memInfo.part_number = mem['PartNumber']
            memInfo.fru_serial_number = mem['SerialNumber']
            memInfo.type = mem['Model']
            memInfo.size = mem['Capacity'] / (1024 * 1024 * 1024)
            
        return result
    
    def load_fan_information(self):
        fanInstances = self.conn.EnumerateInstances('CIM_Fan');
        if (len(fanInstances) == 0):
            raise Exception("No instances of System 'CIM_Fan' found")         
        
        result = []
        for fan in fanInstances :
            
            enable_state = fan['EnabledState']
            if enable_state == CONST_ENABLED:
                fan_sensors = self.conn.Associators(fan.path, AssocClass='CIM_AssociatedSensor', ResultClass='CIM_NumericSensor', Role='Dependent', ResultRole='Antecedent')
                for fan_sensor in fan_sensors:
                    fanInfo = FanInformation()
                    result.append(fanInfo)
                
                    fanInfo.health_state = const_fan_healthstate_dict[fan_sensor['HealthState']]
                
                    status_list = fan_sensor['OperationalStatus']
                    if (len(status_list) > 0):
                        fanInfo.status = const_fan_status_dict[status_list[0]]
                    else:
                        fanInfo.status = const_fan_status_dict[0]
                    
                    fanInfo.fru_name = fan_sensor['ElementName']
                    fanInfo.speed = fan_sensor['CurrentReading']
                    
                    
        return result
        
    def load_powersupply_information(self):
        psInstances = self.conn.EnumerateInstances('CIM_PowerSupply')
        if (len(psInstances) == 0):
            raise Exception("No instances of System 'CIM_PowerSupply' found")  
                   
        result = []
        for ps in psInstances:
            enable_state = ps['EnabledState']
            if enable_state == CONST_ENABLED:
                powerInfo = PowerSupplyInformation()
                result.append(powerInfo)
                
                powerInfo.fru_name = ps['ElementName']
                powerInfo.health_state = const_powersupply_healthstate_dict[ps['HealthState']]
                
                status_list = ps['OperationalStatus']
                if (len(status_list) > 0):
                    powerInfo.status = const_powersupply_status_dict[status_list[0]]
                else:
                    powerInfo.status = const_powersupply_status_dict[0]
                
                powerInfo.rated_power = ps['TotalOutputPower'] / 1000
                
                pkg = self.get_physical_package(ps.path)
                if pkg is not None:
                    powerInfo.manufacturer = pkg.manufacturer
                    powerInfo.part_number = pkg.part_number
                    powerInfo.serial_number = pkg.serial_number
        
        return result     
                
def dump_obj(obj):
    class_name = obj.__class__.__name__
    print("---------- %s -----------" % class_name)        
    for attr in vars(obj):
        print ('%s = %s' % (attr, getattr(obj, attr))) 
          
if __name__ == '__main__':
    cim_svr = ServerCimConnector('http://10.240.212.85:5988', 'USERID', 'PASSW0RD', 'root/cimv2')
    
    print("===================== System Information =====================")
    sysinfo = cim_svr.load_system_information()
    dump_obj(sysinfo)
    print("")
    
    print("===================== Processors =====================")
    processors = cim_svr.load_processor_information()
    for processor in processors:
        dump_obj(processor)
    print("")
    
    
    print("===================== Memories =====================")
    memories = cim_svr.load_memory_information()
    for mem in memories:
        dump_obj(mem)
    print("")
    
    print("===================== Fans =====================")
    fans = cim_svr.load_fan_information()
    for fan in fans:
        dump_obj(fan)
    print("")
    
    print("===================== PowerSupplies =====================")
    powersupplies = cim_svr.load_powersupply_information()
    for power in powersupplies:
        dump_obj(power)
    print("")












