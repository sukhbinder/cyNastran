#pylint: disable=C0301,C0103,W0201,R0911,R0915,R0914
"""
Contains the OES class that is used to read stress/strain data
"""
from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
from struct import Struct

from pyNastran.op2.op2_common import OP2Common
from pyNastran.op2.op2_helper import polar_to_real_imag

from pyNastran.op2.tables.oes_stressStrain.real.oes_bars import RealBarStress, RealBarStrain
from pyNastran.op2.tables.oes_stressStrain.real.oes_beams import RealBeamStress, RealBeamStrain
from pyNastran.op2.tables.oes_stressStrain.real.oes_bush import BushStress, BushStrain
from pyNastran.op2.tables.oes_stressStrain.real.oes_bush1d import RealBush1DStress  # unused
from pyNastran.op2.tables.oes_stressStrain.real.oes_compositePlates import (RealCompositePlateStress, RealCompositePlateStrain,
                                                                            RealCompositePlateStressVector, RealCompositePlateStrainVector)
from pyNastran.op2.tables.oes_stressStrain.real.oes_gap import NonlinearGapStressObject
from pyNastran.op2.tables.oes_stressStrain.real.oes_plates import (RealPlateStress, RealPlateStrain,
                                                                   RealPlateStressVector, RealPlateStrainVector)
from pyNastran.op2.tables.oes_stressStrain.real.oes_rods import (RealRodStress, RealRodStrain,
                                                                 RealRodStressVector, RealRodStrainVector)
from pyNastran.op2.tables.oes_stressStrain.real.oes_shear import (RealShearStress, RealShearStrain,
                                                                  RealShearStrainVector, RealShearStressVector)
from pyNastran.op2.tables.oes_stressStrain.real.oes_solids import (RealSolidStress, RealSolidStrain,
                                                                   RealSolidStrainVector, RealSolidStressVector)
from pyNastran.op2.tables.oes_stressStrain.real.oes_springs import RealCelasStress, RealCelasStrain, NonlinearSpringStress
from pyNastran.op2.tables.oes_stressStrain.real.oes_triax import RealTriaxStress, RealTriaxStrain

from pyNastran.op2.tables.oes_stressStrain.complex.oes_bars import ComplexBarStress, ComplexBarStrain
from pyNastran.op2.tables.oes_stressStrain.complex.oes_bush import ComplexBushStress, ComplexBushStrain
from pyNastran.op2.tables.oes_stressStrain.complex.oes_bush1d import ComplexBush1DStress
from pyNastran.op2.tables.oes_stressStrain.complex.oes_plates import ComplexPlateStress, ComplexPlateStrain
from pyNastran.op2.tables.oes_stressStrain.complex.oes_rods import (ComplexRodStress, ComplexRodStrain)
                                                                    #ComplexRodStressVector, ComplexRodStrainVector)
from pyNastran.op2.tables.oes_stressStrain.complex.oes_shear import ComplexShearStress, ComplexShearStrain
from pyNastran.op2.tables.oes_stressStrain.complex.oes_solids import (ComplexSolidStress, ComplexSolidStrain,
                                                                      ComplexSolidStressVector, ComplexSolidStrainVector)
from pyNastran.op2.tables.oes_stressStrain.complex.oes_springs import ComplexCelasStress, ComplexCelasStrain

from pyNastran.op2.tables.oes_stressStrain.oes_nonlinear import NonlinearRod, NonlinearQuad, HyperelasticQuad


class OES(OP2Common):
    """
    Defines  the OES class that is used to read stress/strain data
    """
    def __init__(self):
        OP2Common.__init__(self)
        self.ntotal = 0

    def _read_oes1_3(self, data):
        """
        reads OES1 subtable 3
        """
        self.words = ['aCode', 'tCode', 'element_type', 'isubcase',
                      '???', '???', '???', 'load_set'
                      'format_code', 'num_wide', 's_code', '???',
                      '???', '???', '???', '???',
                      '???', '???', '???', '???',
                      '???', '???', '???', '???',
                      '???', 'Title', 'subtitle', 'label']

        self.parse_approach_code(data)  # 3

        ## element type
        self.element_type = self.add_data_parameter(data, 'element_type', 'i', 3, False)

        ## load set ID
        self.load_set = self.add_data_parameter(data, 'load_set', 'i', 8, False)

        ## format code
        self.format_code = self.add_data_parameter(data, 'format_code', 'i', 9, False)

        ## number of words per entry in record
        ## .. note:: is this needed for this table ???
        self.num_wide = self.add_data_parameter(data, 'num_wide', 'i', 10, False)

        ## stress/strain codes
        self.s_code = self.add_data_parameter(data, 's_code', 'i', 11, False)

        ## thermal flag; 1 for heat ransfer, 0 otherwise
        self.thermal = self.add_data_parameter(data, 'thermal', 'i', 23, False)

        ## assuming tCode=1
        if self.analysis_code == 1:   # statics / displacement / heat flux
            ## load set number
            self.lsdvmn = self.add_data_parameter(data, 'lsdvmn', 'i', 5, False)
            self.dataNames = self.apply_data_code_value('dataNames', ['lsdvmn'])
            self.setNullNonlinearFactor()
        elif self.analysis_code == 2:  # real eigenvalues
            #: mode number
            self.mode = self.add_data_parameter(data, 'mode', 'i', 5)
            #: real eigenvalue
            self.eigr = self.add_data_parameter(data, 'eigr', 'f', 6, False)
            #: mode or cycle TODO confused on the type - F1 means float/int???
            self.mode2 = self.add_data_parameter(data, 'mode2', 'i', 7, False)
            self.cycle = self.add_data_parameter(data, 'cycle', 'f', 7, False)
            self.dataNames = self.apply_data_code_value('dataNames', ['mode', 'eigr', 'mode2', 'cycle'])
        #elif self.analysis_code==3: # differential stiffness
            #self.lsdvmn = self.get_values(data,'i',5) ## load set number
            #self.data_code['lsdvmn'] = self.lsdvmn
        #elif self.analysis_code==4: # differential stiffness
        #    self.lsdvmn = self.get_values(data,'i',5) ## load set number
        elif self.analysis_code == 5:   # frequency
            ## frequency
            self.freq = self.add_data_parameter(data, 'freq', 'f', 5)
            self.dataNames = self.apply_data_code_value('dataNames', ['freq'])
        elif self.analysis_code == 6:  # transient
            ## time step
            self.dt = self.add_data_parameter(data, 'dt', 'f', 5)
            self.dataNames = self.apply_data_code_value('dataNames', ['dt'])
        elif self.analysis_code == 7:  # pre-buckling
            ## load set
            self.lsdvmn = self.add_data_parameter(data, 'lsdvmn', 'i', 5)
            self.dataNames = self.apply_data_code_value('dataNames', ['lsdvmn'])
        elif self.analysis_code == 8:  # post-buckling
            ## mode number
            self.lsdvmn = self.add_data_parameter(data, 'lsdvmn', 'i', 5)
            self.eigr = self.add_data_parameter(data, 'eigr', 'f', 6, False)  # real eigenvalue
            self.dataNames = self.apply_data_code_value('dataNames', ['lsdvmn', 'eigr'])
        elif self.analysis_code == 9:  # complex eigenvalues
            ## mode number
            self.mode = self.add_data_parameter(data, 'mode', 'i', 5)
            ## real eigenvalue
            self.eigr = self.add_data_parameter(data, 'eigr', 'f', 6, False)
            ## imaginary eigenvalue
            self.eigi = self.add_data_parameter(data, 'eigi', 'f', 7, False)
            self.dataNames = self.apply_data_code_value('dataNames', ['mode', 'eigr', 'eigi'])
        elif self.analysis_code == 10:  # nonlinear statics
            ## load step
            self.lftsfq = self.add_data_parameter(data, 'lftsfq', 'f', 5)
            self.dataNames = self.apply_data_code_value('dataNames', ['lftsfq'])
        elif self.analysis_code == 11:  # old geometric nonlinear statics
            ## load set number
            self.lsdvmn = self.add_data_parameter(data, 'lsdvmn', 'i', 5)
            self.dataNames = self.apply_data_code_value('dataNames', ['lsdvmn'])
        elif self.analysis_code == 12:  # contran ? (may appear as aCode=6)  --> straight from DMAP...grrr...
            ## Time step ??? --> straight from DMAP
            self.dt = self.add_data_parameter(data, 'dt', 'f', 5)
            self.dataNames = self.apply_data_code_value('dataNames', ['dt'])
        else:
            raise RuntimeError('invalid analysis_code...analysis_code=%s' %
                               self.analysis_code)
        # tCode=2
        #if self.analysis_code==2: # sort2
        #    self.lsdvmn = self.get_values(data,'i',5)

        self.element_name = self.element_mapper[self.element_type]
        self.data_code['element_name'] = self.element_name
        #self.log.debug('  element_name=%s-%i  isubcase=%s' % (self.element_name, self.element_type,
        #                                                      self.isubcase))
        if self.debug3():
            self.binary_debug.write('  element_name = %r\n' % self.element_name)
            self.binary_debug.write('  approach_code = %r\n' % self.approach_code)
            self.binary_debug.write('  tCode    = %r\n' % self.tCode)
            self.binary_debug.write('  isubcase = %r\n' % self.isubcase)

        self._read_title(data)
        if self.element_type not in self.element_mapper:
            msg = 'element_type=%s' % self.element_type
            return self._not_implemented_or_skip(data, msg)

        self._write_debug_bits()
        self._parse_stress_code()

    def _parse_stress_code(self):
        """
        s_code =  0 -> stress_bits = [0,0,0,0,0]
        s_code =  1 -> stress_bits = [0,0,0,0,1]
        s_code =  2 -> stress_bits = [0,0,0,1,0]
        s_code =  3 -> stress_bits = [0,0,0,1,1]
        etc.
        s_code = 32 -> stress_bits = [1,1,1,1,1]

        stress_bits[0] = 0 -> isMaxShear=True       isVonMises=False
        stress_bits[0] = 1 -> isMaxShear=False      isVonMises=True

        stress_bits[1] = 0 -> isStress=True         isStrain=False
        stress_bits[2] = 0 -> isFiberCurvature=True isFiberDistance=False
        stress_bits[3] = 0 -> duplicate of Bit[1] (stress/strain)
        stress_bits[4] = 0 -> material coordinate system flag
        """
        bits = [0, 0, 0, 0, 0]

        s_code = self.s_code
        i = 4
        while s_code > 0:
            value = s_code % 2
            s_code = (s_code - value) // 2
            bits[i] = value
            i -= 1
        self.stress_bits = bits
        self.data_code['stress_bits'] = self.stress_bits

    def _read_oes1_4(self, data):
        """
        Reads the Stress/Strain Table 4
        """
        #assert self.isubtable == -4, self.isubtable
        #if self.debug:
            #self.binary_debug.write('  element_name = %r\n' % self.element_name)
        #print "element_name =", self.element_name

        if self.is_sort1():
            n = self._read_oes1_4_sort1(data)
        else:
            msg = 'sort2 Type=%s num=%s' % (self.element_name, self.element_type)
            n = self._not_implemented_or_skip(data, msg)
        return n


    def print_obj_name_on_crash(func):
        """
        Debugging function to print the object name and an needed parameters
        """
        def new_func(self, data):
            """
            The actual function exec'd by the decorated function.
            """
            try:
                n = func(self, data)
            except:
                print("----------")
                print(self.obj)
                print(self.data_code)
                if self.obj is not None:
                    #from pyNastran.utils import object_attributes
                    #print object_attributes(self.obj)
                    print(self.obj.data_code)
                print("----------")
                raise
            return n
        return new_func

    @print_obj_name_on_crash
    def _read_oes1_4_sort1(self, data):
        """
        Reads OES1 subtable 4
        """
        #return len(data)
        assert self.is_sort1() == True
        if self.thermal == 0:
            n = self._read_oes_loads(data)
        elif self.thermal == 1:
            n = self._read_oes_thermal(data)
        else:
            msg = 'thermal=%s' % self.thermal
            n = self._not_implemented_or_skip(data, msg)
        return n

    def _read_oes_thermal(self, data):
        """
        Reads OES self.thermal=1 tables
        """
        return len(data)

    def _read_oes_loads(self, data):
        """
        Reads OES self.thermal=0 stress/strain
        """
        #return len(data)
        n = 0
        is_magnitude_phase = self.is_magnitude_phase()
        dt = self.nonlinear_factor

        if self.element_type in [1, 3, 10]:  # rods
            # 1-CROD
            # 3-CTUBE
            # 10-CONROD

            if self.isStress():
                result_name = 'rodStress'
                slot = self.rodStress
                obj_real = RealRodStress
                obj_complex = ComplexRodStress

                #result_vector_name
                ComplexRodStressVector = None
                obj_vector_real = RealRodStressVector
                obj_vector_complex = ComplexRodStressVector
                if self.element_type == 1: # CROD
                    result_vector_name = 'crod_stress'
                    slot_vector = self.crod_stress
                elif self.element_type == 3:  # CTUBE
                    result_vector_name = 'ctube_stress'
                    slot_vector = self.ctube_stress
                elif self.element_type == 10:  # CONROD
                    result_vector_name = 'conrod_stress'
                    slot_vector = self.conrod_stress
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)
            else:
                result_name = 'rodStrain'
                slot = self.rodStrain
                obj_real = RealRodStrain
                obj_complex = ComplexRodStrain

                #result_vector_name
                ComplexRodStrainVector = None
                obj_vector_real = RealRodStrainVector
                obj_vector_complex = ComplexRodStrainVector
                if self.element_type == 1: # CROD
                    result_vector_name = 'crod_strain'
                    slot_vector = self.crod_strain
                elif self.element_type == 3:  # CTUBE
                    result_vector_name = 'ctube_strain'
                    slot_vector = self.ctube_strain
                elif self.element_type == 10:  # CONROD
                    result_vector_name = 'conrod_strain'
                    slot_vector = self.conrod_strain
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)

            if self.format_code == 1 and self.num_wide == 5:  # real
                ntotal = 5 * 4
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_real, obj_vector_real)
                if auto_return:
                    return nelements * self.num_wide * 4

                if self.debug:
                    self.binary_debug.write('  [cap, element1, element2, ..., cap]\n')
                    self.binary_debug.write('  cap = %i  # assume 1 cap when there could have been multiple\n' % len(data))
                    self.binary_debug.write('  #elementi = [eid_device, axial, axial_margin, torsion, torsion_margin]\n')
                    self.binary_debug.write('  nelements=%i; nnodes=1 # centroid\n' % nelements)

                s = Struct(b'i4f')
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]
                    out = s.unpack(edata)
                    (eid_device, axial, axial_margin, torsion, torsion_margin) = out
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('  eid=%i; C=[%s]\n' % (eid, ', '.join(['%r' % di for di in out])))
                    assert eid > 0, eid
                    self.obj.add_new_eid(dt, eid, axial, axial_margin, torsion, torsion_margin)
                    n += ntotal
            elif self.format_code in [2, 3] and self.num_wide == 5: # imag
                ntotal = 20
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_complex, obj_vector_complex)
                if auto_return:
                    return nelements * self.num_wide * 4

                s = Struct(b'i4f')
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    (eid_device, axialReal, axial_imag, torsion_real, torsionImag) = s.unpack(edata)
                    eid = (eid_device - self.device_code) // 10

                    if is_magnitude_phase:
                        axial = polar_to_real_imag(axialReal, axial_imag)
                        torsion = polar_to_real_imag(torsion_real, torsionImag)
                    else:
                        axial = complex(axialReal, axial_imag)
                        torsion = complex(torsion_real, torsionImag)
                    assert eid > 0, eid

                    #print "out = ",out
                    self.obj.add_new_eid(dt, eid, axial, torsion)
                    n += ntotal
            #elif self.format_code in [2, 3] and self.num_wide == 8:  # is this imag ???
                #ntotal = 32
                #s = Struct(b'i')
                #nelements = len(data) // ntotal
                #for i in xrange(nelements):
                    #edata = data[n:n + 4]
                    #eid_device, = s.unpack(edata)
                    #eid = (eid_device - self.device_code) // 10
                    #assert eid > 0, eid
                    #n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type == 2: # CBEAM
            # 2-CBEAM
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 111:  # real
                ntotal = 444 # 44 + 10*40  (11 nodes)
                if self.isStress():
                    self.create_transient_object(self.beamStress, RealBeamStress)
                else:
                    self.create_transient_object(self.beamStrain, RealBeamStrain)

                nelements = len(data) // ntotal
                s = Struct(b'i')

                nnodes = 10  # 11-1
                #ntotal = self.obj.getLengthTotal()
                ntotal = self.num_wide * 4
                n1 = 44
                n2 = 40
                s1 = Struct(b'ii9f')
                s2 = Struct(b'i9f')

                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+n1]
                    n += n1

                    out = s1.unpack(edata)
                    eid_device = out[0]
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('CBEAM-2 - eid=%i out=%s\n' % (eid, str(out)))

                    #(grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
                    self.obj.add_new_eid(dt, eid, out[1:])

                    for inode in xrange(nnodes):
                        edata = data[n:n+n2]
                        n += n2
                        out = s2.unpack(edata)
                        # (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
                        self.obj.add(dt, eid, out)
                    #print "eid=%i axial=%i torsion=%i" % (eid, axial, torsion)
            elif self.format_code in [2, 3] and self.num_wide == 111:  # imag and random?
                ntotal = 444 # 44 + 10*40  (11 nodes)
                #if self.isStress():
                    #self.create_transient_object(self.beamStress, RealBeamStress)
                #else:
                    #self.create_transient_object(self.beamStrain, RealBeamStrain)

                nelements = len(data) // ntotal
                s = Struct(b'i')

                nnodes = 10  # 11-1
                #ntotal = self.obj.getLengthTotal()
                ntotal = self.num_wide * 4
                n1 = 44
                n2 = 40
                s1 = Struct(b'ii9f')
                s2 = Struct(b'i9f')

                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+n1]
                    n += n1

                    out = s1.unpack(edata)
                    eid_device = out[0]
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('CBEAM-2 - eid=%i out=%s\n' % (eid, str(out)))

                    #(grid, sd, ercr, exdr, exer, exfr,
                    #           exci, exdi, exei, exfi) = out
                    #self.obj.add_new_eid(dt, eid, out[1:])

                    for inode in xrange(nnodes):
                        edata = data[n:n+n2]
                        n += n2
                        out = s2.unpack(edata)
                        #self.obj.add(dt, eid, out)
                    #print "eid=%i axial=%i torsion=%i" % (eid, axial, torsion)
                return len(data)
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type == 4: # CSHEAR
            # 4-CSHEAR
            if self.isStress():
                result_name = 'shearStress'
                slot = self.shearStress
                obj_real = RealShearStress
                obj_complex = ComplexShearStress

                #result_vector_name
                ComplexShearStressVector = None
                obj_vector_real = RealShearStressVector
                obj_vector_complex = ComplexShearStressVector
                result_vector_name = 'cshear_stress'
                slot_vector = self.cshear_stress
            else:
                result_name = 'shearStrain'
                slot = self.shearStrain
                obj_real = RealShearStrain
                obj_complex = ComplexShearStrain

                #result_vector_name
                #slot_vector
                ComplexShearStrainVector = None
                obj_vector_real = RealShearStrainVector
                obj_vector_complex = ComplexShearStrainVector
                result_vector_name = 'cshear_strain'
                slot_vector = self.cshear_strain

            if self.format_code == 1 and self.num_wide == 4:  # real
                ntotal = 16  # 4*4
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_real, obj_vector_real)
                if auto_return:
                    return nelements * self.num_wide * 4

                s = Struct(b'i3f')
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)  # num_wide=5
                    if self.debug4():
                        self.binary_debug.write('CSHEAR-4 - %s\n' % str(out))

                    (eid_device, max_strain, avg_strain, margin) = out
                    eid = (eid_device - self.device_code) // 10
                    self.obj.add_new_eid(dt, eid, max_strain, avg_strain, margin)
                    n += ntotal

            elif self.format_code in [2, 3] and self.num_wide == 5:  # imag
                ntotal = 20  # 4*5
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_complex, obj_vector_complex)
                if auto_return:
                    return nelements * self.num_wide * 4

                s = Struct(b'i4f')
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)  # num_wide=5
                    if self.debug4():
                        self.binary_debug.write('CSHEAR-4 - %s\n' % str(out))
                    (eid_device, etmaxr, etmaxi, etavgr, etavgi) = out
                    eid = (eid_device - self.device_code) // 10

                    if is_magnitude_phase:
                        etmax = polar_to_real_imag(etmaxr, etmaxi)
                        etavg = polar_to_real_imag(etavgr, etavgi)
                    else:
                        etmax = complex(etmaxr, etmaxi)
                        etavg = complex(etavgr, etavgi)
                    self.obj.add_new_eid_sort1(dt, eid, (etmax, etavg))
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [11, 12, 13, 14]:  # springs
            # 11-CELAS1
            # 12-CELAS2
            # 13-CELAS3
            # 14-CELAS4
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 2:  # real
                if self.isStress():
                    self.create_transient_object(self.celasStress, RealCelasStress)
                else:
                    self.create_transient_object(self.celasStrain, RealCelasStrain)
                ntotal = 8 # 2 * 4
                nelements = len(data) // ntotal
                s = Struct(b'if')
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]
                    out = s.unpack(edata)
                    (eid_device, ox) = out
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('  eid=%i result%i=[%i, %f]\n' % (eid, i, eid_device, ox))
                    self.obj.add_new_eid(dt, eid, (ox,))
                    n += ntotal
            elif self.format_code in [2, 3] and self.num_wide == 3:  # imag
                if self.isStress():
                    self.create_transient_object(self.celasStress, ComplexCelasStress)
                else:
                    self.create_transient_object(self.celasStrain, ComplexCelasStrain)
                ntotal = 12
                s = Struct(b'i2f')
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    (eid_device, axial_real, axial_imag) = s.unpack(edata)
                    eid = (eid_device - self.device_code) // 10

                    if is_magnitude_phase:
                        axial = polar_to_real_imag(axial_real, axial_imag)
                    else:
                        axial = complex(axial_real, axial_imag)

                    if self.debug4():
                        self.binary_debug.write('  eid=%i result%i=[%i, %f, %f]\n' % (eid, i, eid_device, axial_real, axial_imag))
                    assert eid > 0
                    self.obj.add_new_eid_sort1(dt, eid, axial)
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type == 34: # CBAR
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 16:  # real
                if self.isStress():
                    self.create_transient_object(self.barStress, RealBarStress)
                else:
                    self.create_transient_object(self.barStrain, RealBarStrain)
                ntotal = 16 * 4
                nelements = len(data) // ntotal
                if self.debug:
                    self.binary_debug.write('  [cap, element1, element2, ..., cap]\n')
                    #self.binary_debug.write('  cap = %i  # assume 1 cap when there could have been multiple\n' % len(data))
                    self.binary_debug.write('  #elementi = [eid_device, s1a, s2a, s3a, s4a, axial, smaxa, smina, MSt,\n')
                    self.binary_debug.write('                           s1b, s2b, s3b, s4b, smaxb, sminb,        MSc]\n')
                    self.binary_debug.write('  nelements=%i; nnodes=1 # centroid\n' % nelements)

                s = Struct(b'i15f')
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]
                    out = s.unpack(edata)
                    (eid_device, s1a, s2a, s3a, s4a, axial, smaxa, smina, MSt,
                                 s1b, s2b, s3b, s4b, smaxb, sminb, MSc) = out
                    eid = (eid_device - self.device_code) // 10
                    assert eid > 0, eid
                    if self.debug4():
                        self.binary_debug.write('  eid=%i; C%i=[%s]\n' % (eid, i, ', '.join(['%r' % di for di in out])))
                    n += ntotal
                    self.obj.add_new_eid(self.element_name, dt, eid,
                                         s1a, s2a, s3a, s4a, axial, smaxa, smina, MSt,
                                         s1b, s2b, s3b, s4b,        smaxb, sminb, MSc)
            elif self.format_code in [2, 3] and self.num_wide == 19:  # imag
                if self.isStress():
                    self.create_transient_object(self.barStress, ComplexBarStress)
                else:
                    self.create_transient_object(self.barStrain, ComplexBarStrain)

                s = Struct(b'i18f')
                ntotal = 76
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]
                    n += ntotal
                    out = s.unpack(edata)
                    (eid_device, s1ar, s2ar, s3ar, s4ar, axialr,
                                 s1ai, s2ai, s3ai, s4ai, axiali,
                                 s1br, s2br, s3br, s4br,
                                 s1bi, s2bi, s3bi, s4bi) = out

                    eid = (eid_device - self.device_code) // 10
                    assert eid > 0, eid
                    if is_magnitude_phase:
                        s1a = polar_to_real_imag(s1ar, s1ai)
                        s1b = polar_to_real_imag(s1br, s1bi)
                        s2a = polar_to_real_imag(s2ar, s2ai)
                        s2b = polar_to_real_imag(s2br, s2bi)
                        s3a = polar_to_real_imag(s3ar, s3ai)
                        s3b = polar_to_real_imag(s3br, s3bi)
                        s4a = polar_to_real_imag(s4ar, s4ai)
                        s4b = polar_to_real_imag(s4br, s4bi)
                        axial = polar_to_real_imag(axialr, axiali)
                    else:
                        s1a = complex(s1ar, s1ai)
                        s1b = complex(s1br, s1bi)
                        s2a = complex(s2ar, s2ai)
                        s2b = complex(s2br, s2bi)
                        s3a = complex(s3ar, s3ai)
                        s3b = complex(s3br, s3bi)
                        s4a = complex(s4ar, s4ai)
                        s4b = complex(s4br, s4bi)
                        axial = complex(axialr, axiali)

                    self.obj.add_new_eid('CBAR', dt, eid, s1a, s2a, s3a, s4a, axial,
                                                          s1b, s2b, s3b, s4b)
                    #print("eid=%i s1=%i s2=%i s3=%i s4=%i axial=%-5i" % (eid,s1a,s2a,s3a,s4a,axial))
                    #print("         s1=%i s2=%i s3=%i s4=%i"          % (s1b,s2b,s3b,s4b))
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [39, 67, 68]: # solid stress
            # 39-CTETRA
            # 67-CHEXA
            # 68-CPENTA
            if self.isStress():
                result_name = 'solidStress'
                slot = self.solidStress
                obj_real = RealSolidStress
                obj_complex = ComplexSolidStress

                #result_vector_name
                #slot_vector
                obj_vector_real = RealSolidStressVector
                obj_vector_complex = ComplexSolidStressVector
                if self.element_type == 39: # CTETRA
                    nnodes_expected = 5  # 1 centroid + 4 corner points
                    result_vector_name = 'ctetra_stress'
                    slot_vector = self.ctetra_stress
                    element_name = 'CTETRA4'
                elif self.element_type == 67:  # CHEXA
                    nnodes_expected = 9
                    result_vector_name = 'chexa_stress'
                    slot_vector = self.chexa_stress
                    element_name = 'CHEXA8'
                elif self.element_type == 68:  # CPENTA
                    nnodes_expected = 7
                    result_vector_name = 'cpenta_stress'
                    slot_vector = self.cpenta_stress
                    element_name = 'CPENTA6'
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)
            else:
                result_name = 'solidStrain'
                slot = self.solidStrain
                obj_real = RealSolidStrain
                obj_complex = ComplexSolidStrain

                #result_vector_name
                #slot_vector
                obj_vector_real = RealSolidStrainVector
                obj_vector_complex = ComplexSolidStrainVector
                if self.element_type == 39: # CTETRA
                    nnodes_expected = 5  # 1 centroid + 4 corner points
                    result_vector_name = 'ctetra_strain'
                    slot_vector = self.ctetra_strain
                    element_name = 'CTETRA4'
                elif self.element_type == 67:  # CHEXA
                    nnodes_expected = 9
                    result_vector_name = 'chexa_strain'
                    slot_vector = self.chexa_strain
                    element_name = 'CHEXA8'
                elif self.element_type == 68:  # CPENTA
                    nnodes_expected = 7
                    result_vector_name = 'cpenta_strain'
                    slot_vector = self.cpenta_strain
                    element_name = 'CPENTA6'
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)

            numwide_real = 4 + 21 * nnodes_expected
            numwide_imag = 4 + (17 - 4) * nnodes_expected
            preline1 = '%s-%s' % (self.element_name, self.element_type)
            preline2 = ' ' * len(preline1)
            #print "_data_factor =", self._data_factor
            self._data_factor = nnodes_expected
            if self.format_code == 1 and self.num_wide == numwide_real:  # real
                ntotal = 16 + 84 * nnodes_expected
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_real, obj_vector_real)
                if auto_return:
                    return nelements * self.num_wide * 4

                struct1 = Struct(b'ii4si')
                struct2 = Struct(b'i20f')
                for i in xrange(nelements):
                    edata = data[n:n+16]
                    out = struct1.unpack(edata)
                    (eid_device, cid, abcd, nnodes) = out
                    eid = (eid_device - self.device_code) // 10

                    if self.debug4():
                        self.binary_debug.write('%s - eid=%i; %s\n' % (preline1, eid, str(out)))

                    #print "abcd = %r" % abcd
                    #print "eid=%s cid=%s nNodes=%s nNodesExpected=%s" % (eid,cid,nNodes,nNodesExpected)

                    assert nnodes < 21, 'print_block(data[n:n+16])'  #self.print_block(data[n:n+16])

                    n += 16
                    for inode in xrange(nnodes_expected):  # nodes pts, +1 for centroid (???)
                        out = struct2.unpack(data[n:n + 84]) # 4*21 = 84
                        if self.debug4():
                            self.binary_debug.write('%s - %s\n' % (preline2, str(out)))
                        (grid_device, sxx, sxy, s1, a1, a2, a3, pressure, svm,
                                      syy, syz, s2, b1, b2, b3,
                                      szz, sxz, s3, c1, c2, c3) = out

                        #if self.debug4():
                            #self.binary_debug.write('  eid=%s inode=%i; C=[%s]\n' % (eid, nodeID, ', '.join(['%r' % di for di in out]) ))

                        if grid_device == 0:
                            grid = 'CENTER'
                        else:
                            #grid = (grid_device - device_code) // 10
                            grid = grid_device

                        #smax = max(s1, s2, s3)
                        #smin = min(s1, s2, s3)

                        aCos = [a1, a2, a3]
                        bCos = [b1, b2, b3]
                        cCos = [c1, c2, c3]
                        if inode == 0:
                            #element_name = self.element_name+str(nnodes) #  this is correct, but fails
                            self.obj.add_eid(element_name, cid, dt, eid, grid,
                                             sxx, syy, szz, sxy, syz, sxz, s1, s2, s3,
                                             aCos, bCos, cCos, pressure, svm)
                        else:
                            self.obj.add_node(dt, eid, inode, grid,
                                              sxx, syy, szz, sxy, syz, sxz, s1, s2, s3,
                                              aCos, bCos, cCos, pressure, svm)
                        n += 84

            elif self.format_code in [2, 3] and self.num_wide == numwide_imag:  # complex
                ntotal = numwide_imag * 4
                #nelements = len(data) / float(ntotal)
                nelements = len(data) // ntotal
                result_name = 'solidStresss' if self.isStress() else 'solidStrain'
                result_name += '_subcase%i' % self.isubcase
                self.ntotal += nelements * nnodes_expected
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_complex, obj_vector_complex)
                if auto_return:
                    return nelements * self.num_wide * 4


                #print "self.obj.data.shape =", self.obj.data.shape
                s1 = Struct(b'2i4si')
                s2 = Struct(b'i12f')
                for i in xrange(nelements):
                    edata = data[n:n+16]
                    n += 16
                    out = s1.unpack(edata)
                    (eid_device, cid, ctype, nodef) = out
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('  eid=%i C=[%s]\n' % (eid, ', '.join(['%r' % di for di in out])))
                    assert eid > 0, eid

                    #element_name = self.element_name + str(nodef)  # this is correct, but has problems...
                    self.obj.add_eid_sort1(self.element_type, element_name, dt, eid, cid, ctype, nodef)
                    for inode in xrange(nnodes_expected):
                        edata = data[n:n+52]
                        n += 52
                        out = s2.unpack(edata)
                        (grid, exr, eyr, ezr, etxyr, etyzr, etzxr,
                               exi, eyi, ezi, etxyi, etyzi, etzxi) = out
                        #if grid == 0:
                            #grid = 'CENTER'

                        if is_magnitude_phase:
                            ex = polar_to_real_imag(exr, exi)
                            ey = polar_to_real_imag(eyr, eyi)
                            ez = polar_to_real_imag(ezr, ezi)
                            etxy = polar_to_real_imag(etxyr, etxyi)
                            etyz = polar_to_real_imag(etyzr, etyzi)
                            etzx = polar_to_real_imag(etzxr, etzxi)
                        else:
                            ex = complex(exr, exi)
                            ey = complex(eyr, eyi)
                            ez = complex(ezr, ezi)
                            etxy = complex(etxyr, etxyi)
                            etyz = complex(etyzr, etyzi)
                            etzx = complex(etzxr, etzxi)

                        if self.debug4():
                            self.binary_debug.write('       node%s=[%s]\n' % (grid, ', '.join(['%r' % di for di in out])))
                        #self.obj.add(dt, eid, grid, ex, ey, ez, etxy, etyz, etzx)
                        self.obj.add_node_sort1(dt, eid, grid, inode,
                                                ex, ey, ez, etxy, etyz, etzx)
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        #=========================
        # plates
        elif self.element_type in [33]:  # CQUAD4-centroidal
            # 33-QUAD4-centroidal
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 17:  # real
                if self.isStress():
                    self.create_transient_object(self.plateStress, RealPlateStress)
                else:
                    self.create_transient_object(self.plateStrain, RealPlateStrain)

                #return
                ntotal = 68  # 4*17
                s = Struct(b'i16f')
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]
                    out = s.unpack(edata)

                    (eid_device, fd1, sx1, sy1, txy1, angle1, major1, minor1, max_shear1,
                                 fd2, sx2, sy2, txy2, angle2, major2, minor2, max_shear2) = out

                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('  eid=%i C=[%s]\n' % (eid, ', '.join(['%r' % di for di in out])))

                    self.obj.add_new_eid('CQUAD4', dt, eid, 'CEN/4', fd1, sx1, sy1,
                                       txy1, angle1, major1, minor1, max_shear1)
                    self.obj.add(dt, eid, 'CEN/4', fd2, sx2, sy2, txy2,
                                 angle2, major2, minor2, max_shear2)
                    #print "eid =", eid
                    n += ntotal
            elif self.format_code in [2, 3] and self.num_wide == 15:  # imag
                if self.isStress():
                    self.create_transient_object(self.plateStress, ComplexPlateStress)
                else:
                    self.create_transient_object(self.plateStress, ComplexPlateStress)
                s1 = Struct(b'i14f')
                s2 = Struct(b'i14f')
                nnodes = 0  # centroid + 4 corner points

                ntotal = 4 * (15 * (nnodes + 1))
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+60]  # 4*15=60
                    n += 60
                    out = s1.unpack(edata)  # 15
                    (eid_device, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                                 fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('  eid=%i C=%s\n' % (eid, str(out)))

                    if is_magnitude_phase:
                        sx1 = polar_to_real_imag(sx1r, sx1i)
                        sx2 = polar_to_real_imag(sx2r, sx2i)
                        sy1 = polar_to_real_imag(sy1r, sy1i)
                        sy2 = polar_to_real_imag(sy2r, sy2i)
                        txy1 = polar_to_real_imag(txy1r, txy1i)
                        txy2 = polar_to_real_imag(txy2r, txy2i)
                    else:
                        sx1 = complex(sx1r, sx1i)
                        sx2 = complex(sx2r, sx2i)
                        sy1 = complex(sy1r, sy1i)
                        sy2 = complex(sy2r, sy2i)
                        txy1 = complex(txy1r, txy1i)
                        txy2 = complex(txy2r, txy2i)

                    self.obj.add_new_eid('CQUAD4', dt, eid, 'CEN/4', fd1, sx1, sy1, txy1)
                    self.obj.add(dt, eid, 'CEN/4', fd2, sx2, sy2, txy2)

                    for node_id in xrange(nnodes):  # nodes pts
                        edata = data[n:n+60]  # 4*15=60
                        n += 60
                        out = s2.unpack(edata)
                        if self.debug4():
                            self.binary_debug.write('  %s\n' % str(out))
                        (grid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                               fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

                        if is_magnitude_phase:
                            sx1 = polar_to_real_imag(sx1r, sx1i)
                            sx2 = polar_to_real_imag(sx2r, sx2i)
                            sy1 = polar_to_real_imag(sy1r, sy1i)
                            sy2 = polar_to_real_imag(sy2r, sy2i)
                            txy1 = polar_to_real_imag(txy1r, txy1i)
                            txy2 = polar_to_real_imag(txy2r, txy2i)
                        else:
                            sx1 = complex(sx1r, sx1i)
                            sx2 = complex(sx2r, sx2i)
                            sy1 = complex(sy1r, sy1i)
                            sy2 = complex(sy2r, sy2i)
                            txy1 = complex(txy1r, txy1i)
                            txy2 = complex(txy2r, txy2i)

                        self.obj.addNewNode(dt, eid, grid, fd1, sx1, sy1, txy1)
                        self.obj.add(dt, eid, grid, fd2, sx2, sy2, txy2)
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [74]:  # TRIA3
            if self.isStress():
                result_name = 'plateStress'
                slot = self.plateStress
                obj_real = RealPlateStress
                obj_complex = ComplexPlateStress

                #result_vector_name
                ComplexPlateStressVector = None
                obj_vector_real = RealPlateStressVector
                obj_vector_complex = ComplexPlateStressVector
                if self.element_type == 74: # CTRIA3
                    result_vector_name = 'ctria3_stress'
                    slot_vector = self.ctria3_stress
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)
            else:
                result_name = 'plateStress'
                slot = self.plateStress
                obj_real = RealPlateStrain
                obj_complex = ComplexPlateStrain

                #result_vector_name
                ComplexPlateStrainVector = None
                obj_vector_real = RealPlateStrainVector
                obj_vector_complex = ComplexPlateStrainVector
                if self.element_type == 74: # CTRIA3
                    result_vector_name = 'ctria3_strain'
                    slot_vector = self.ctria3_strain
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)

            if self.format_code == 1 and self.num_wide == 17:  # real
                ntotal = 68  # 4*17
                nelements = len(data) // ntotal
                nlayers = nelements * 2  # 2 layers per node
                auto_return = self._create_oes_object2(nlayers,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_real, obj_vector_real)
                if auto_return:
                    self._data_factor = 2
                    return nelements * self.num_wide * 4

                s = Struct(b'i16f')
                if self.debug:
                    self.binary_debug.write('  [cap, element1, element2, ..., cap]\n')
                    self.binary_debug.write('  cap = %i  # assume 1 cap when there could have been multiple\n' % len(data))
                    self.binary_debug.write('  #elementi = [eid_device, fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,\n')
                    self.binary_debug.write('  #                        fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2,]\n')
                    self.binary_debug.write('  nelements=%i; nnodes=1 # centroid\n' % nelements)

                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)

                    (eid_device, fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,
                                 fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2,) = out
                    eid = (eid_device - self.device_code) // 10

                    if self.debug4():
                        self.binary_debug.write('  OES CTRIA3-74 - eid=%i; C=[%s]\n' % (eid, ', '.join(['%r' % di for di in out])))

                    self.obj.add_new_eid('CTRIA3', dt, eid, 'CEN/3', fd1, sx1, sy1,
                                         txy1, angle1, major1, minor1, vm1)
                    self.obj.add(dt, eid, 'CEN/3', fd2, sx2, sy2, txy2,
                                 angle2, major2, minor2, vm2)
                    #add_the_obj
                    #print "eid =", eid
                    n += ntotal
            elif self.format_code in [2, 3] and self.num_wide == 15:  # imag
                ntotal = 60  # 4*15
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_complex, obj_vector_complex)
                if auto_return:
                    return nelements * self.num_wide * 4

                s = Struct(b'i14f')
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)
                    (eid_device, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                                 fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i,) = out
                    eid = (eid_device - self.device_code) // 10

                    if self.debug4():
                        self.binary_debug.write('  OESC CTRIA3-74 - eid=%i; C=[%s]\n' % (eid, ', '.join(['%r' % di for di in out])))

                    if is_magnitude_phase:
                        sx1 = polar_to_real_imag(sx1r, sx1i)
                        sy1 = polar_to_real_imag(sy1r, sy1i)
                        sx2 = polar_to_real_imag(sx2r, sx2i)
                        sy2 = polar_to_real_imag(sy2r, sy2i)
                        txy1 = polar_to_real_imag(txy1r, txy1i)
                        txy2 = polar_to_real_imag(txy2r, txy2i)
                    else:
                        sx1 = complex(sx1r, sx1i)
                        sy1 = complex(sy1r, sy1i)
                        sx2 = complex(sx2r, sx2i)
                        sy2 = complex(sy2r, sy2i)
                        txy1 = complex(txy1r, txy1i)
                        txy2 = complex(txy2r, txy2i)
                    self.obj.add_new_eid('CTRIA3', dt, eid, 'CEN/3', fd1, sx1, sy1, txy1)
                    self.obj.add(dt, eid, 'CEN/3', fd2, sx2, sy2, txy2)
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [64, 70, 75, 82, 144]:  # bilinear plates
        #elif self.element_type in [64, 70, 75, 82, 144]:  # bilinear plates
            # 64-CQUAD8
            # 70-CTRIAR
            # 75-CTRIA6
            # 82-CQUADR
            # 144-CQUAD4-bilinear
            #print "================================================"
            if self.isStress():
                result_name = 'plateStress'
                slot = self.plateStress
                obj_real = RealPlateStress
                obj_complex = ComplexPlateStrain

                #result_vector_name
                ComplexPlateStressVector = None
                obj_vector_real = RealPlateStressVector
                obj_vector_complex = ComplexPlateStressVector
                # 64-CQUAD8
                # 70-CTRIAR
                # 75-CTRIA6
                # 82-CQUADR
                # 144-CQUAD4-bilinear
                if self.element_type == 64: # CQUAD8
                    result_vector_name = 'cquad8_stress'
                    slot_vector = self.cquad8_stress
                    gridC = 'CEN/8'
                elif self.element_type == 70:  # CTRIAR
                    result_vector_name = 'ctriar_stress'
                    slot_vector = self.ctriar_stress
                    gridC = 'CEN/3'
                elif self.element_type == 75:  # CTRIA6
                    result_vector_name = 'ctria6_stress'
                    slot_vector = self.ctria6_stress
                    gridC = 'CEN/6'
                elif self.element_type == 82:  # CTRIA6
                    result_vector_name = 'cquadr_stress'
                    slot_vector = self.cquadr_stress
                    gridC = 'CEN/4'
                elif self.element_type == 144:  # CQUAD4-bilinear
                    # there's no nead to separate this with centroidal strain
                    # because you can only have one in a given OP2
                    result_vector_name = 'cquad4_stress'
                    slot_vector = self.cquad4_stress
                    gridC = 'CEN/4'
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)
            else:
                result_name = 'plateStrain'
                slot = self.plateStrain
                obj_real = RealPlateStrain
                obj_complex = ComplexPlateStrain

                #result_vector_name
                ComplexPlateStrainVector = None
                obj_vector_real = RealPlateStrainVector
                obj_vector_complex = ComplexPlateStrainVector
                if self.element_type == 64: # CQUAD8
                    result_vector_name = 'cquad8_strain'
                    slot_vector = self.cquad8_strain
                    gridC = 'CEN/8'
                elif self.element_type == 70:  # CTRIAR
                    result_vector_name = 'ctriar_strain'
                    slot_vector = self.ctriar_strain
                    gridC = 'CEN/3'
                elif self.element_type == 75:  # CTRIA6
                    result_vector_name = 'ctria6_strain'
                    slot_vector = self.ctria6_strain
                    gridC = 'CEN/6'
                elif self.element_type == 82: # CQUADR
                    result_vector_name = 'cquadr_strain'
                    slot_vector = self.cquadr_strain
                    gridC = 'CEN/4'
                elif self.element_type == 144: # CQUAD4-bilinear
                    # there's no nead to separate this with centroidal strain
                    # because you can only have one in a given OP2
                    result_vector_name = 'cquad4_strain'
                    slot_vector = self.cquad4_strain
                    gridC = 'CEN/4'
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)

            if self.element_type in [64, 82, 144]:
                nnodes = 4 # + 1 centroid
            elif self.element_type in [70, 75]:
                nnodes = 3 # + 1 centroid
            else:
                msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                return self._not_implemented_or_skip(data, msg)

            numwide_real = 2 + 17 * (nnodes + 1)
            numwide_imag = 2 + 15 * (nnodes + 1)

            etype = self.element_name
            #print "result_name =", result_name, result_vector_name
            #gridC = 'CEN/%i' % nnodes
            if self.format_code == 1 and self.num_wide == numwide_real:  # real
                ntotal = 4 * (2 + 17 * (nnodes + 1))
                nelements = len(data) // ntotal
                nlayers = 2 * nelements * (nnodes + 1)  # 2 layers per node
                #print 'nlayers =', nlayers
                self._data_factor = 10
                auto_return = self._create_oes_object2(nlayers,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_real, obj_vector_real)
                if auto_return:
                    return nelements * self.num_wide * 4

                #assert ntotal == 348, ntotal
                center_format = b'i4si16f'
                node_format = b'i16f'
                cs = Struct(center_format)
                ns = Struct(node_format)

                if self.debug:
                    self.binary_debug.write('  [cap, element1, element2, ..., cap]\n')
                    self.binary_debug.write('  cap = %i  # assume 1 cap when there could have been multiple\n' % len(data))
                    self.binary_debug.write('  #elementi = [centeri, node1i, node2i, node3i, node4i]\n')
                    self.binary_debug.write('  #centeri = [eid_device, j, grid, fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,\n')
                    self.binary_debug.write('  #                                fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2,)]\n')
                    self.binary_debug.write('  #nodeji = [grid, fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,\n')
                    self.binary_debug.write('  #                fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2,)]\n')
                    self.binary_debug.write('  nelements=%i; nnodes=%i # +1 centroid\n' % (nelements, nnodes))

                for i in xrange(nelements):
                    edata = data[n:n+76]

                    out = cs.unpack(edata)  # len=17*4
                    # j is the number of nodes, so CQUAD4 -> 4, but we don't need to save it...
                    (eid_device, j, grid, fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,
                                          fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2,) = out
                    eid = (eid_device - self.device_code) // 10

                    if self.debug4():
                        self.binary_debug.write('  eid=%i; C=[%s]\n' % (eid, ', '.join(['%r' % di for di in out])))

                    #print "eid=%i grid=%s fd1=%i sx1=%i sy1=%i txy1=%i angle1=%i major1=%i minor1=%i vm1=%i" % (eid,grid,fd1,sx1,sy1,txy1,angle1,major1,minor1,vm1)
                    #print "               fd2=%i sx2=%i sy2=%i txy2=%i angle2=%i major2=%i minor2=%i vm2=%i\n"        % (fd2,sx2,sy2,txy2,angle2,major2,minor2,vm2)
                    self.obj.add_new_eid(etype, dt, eid, gridC, fd1, sx1, sy1,
                                         txy1, angle1, major1, minor1, vm1)
                    self.obj.add(dt, eid, gridC, fd2, sx2, sy2, txy2,
                                 angle2, major2, minor2, vm2)
                    n += 76
                    for inode in range(nnodes):
                        out = ns.unpack(data[n:n + 68])
                        (grid, fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,
                               fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2,) = out

                        if self.debug4():
                            d = tuple([grid,
                                      fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,
                                      fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2])
                            self.binary_debug.write('  node%i = [%s]\n' % (inode+1, ', '.join(['%r' % di for di in d])))
                        assert isinstance(grid, int), grid
                        assert grid > 0, grid

                        #print "eid=%i grid=%i fd1=%i sx1=%i sy1=%i txy1=%i angle1=%i major1=%i minor1=%i vm1=%i" % (eid,grid,fd1,sx1,sy1,txy1,angle1,major1,minor1,vm1)
                        #print "               fd2=%i sx2=%i sy2=%i txy2=%i angle2=%i major2=%i minor2=%i vm2=%i\n"        % (fd2,sx2,sy2,txy2,angle2,major2,minor2,vm2)
                        self.obj.addNewNode(dt, eid, grid, fd1, sx1, sy1,
                                            txy1, angle1, major1, minor1, vm1)
                        self.obj.add(dt, eid, grid, fd2, sx2, sy2,
                                     txy2, angle2, major2, minor2, vm2)
                        n += 68
            elif self.format_code in [2, 3] and self.num_wide == numwide_imag:  # imag
                ntotal = numwide_imag * 4
                assert self.num_wide * 4 == ntotal, 'numwide*4=%s ntotal=%s' % (self.num_wide*4, ntotal)
                nelements = len(data) // ntotal
                #if 1:
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_complex, obj_vector_complex)
                if auto_return:
                    return nelements * ntotal

                s1 = Struct(b'ii')  # 2
                s2 = Struct(b'i14f') # 15
                for i in xrange(nelements):
                    (eid_device, _) = s1.unpack(data[n:n+8])
                    n += 8

                    eid = (eid_device - self.device_code) // 10
                    assert eid > 0, eid
                    edata = data[n:n+60]  # 4*15
                    n += 60
                    out = s2.unpack(edata)  # len=15*4
                    if self.debug4():
                        self.binary_debug.write('%s\n' % (str(out)))
                    (grid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                           fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out
                    #gridC = 'CEN/%i' % grid   # this is correct, but fails

                    if is_magnitude_phase:
                        sx1 = polar_to_real_imag(sx1r, sx1i)
                        sy1 = polar_to_real_imag(sy1r, sy1i)
                        sx2 = polar_to_real_imag(sx2r, sx2i)
                        sy2 = polar_to_real_imag(sy2r, sy2i)
                        txy1 = polar_to_real_imag(txy1r, txy1i)
                        txy2 = polar_to_real_imag(txy2r, txy2i)
                    else:
                        sx1 = complex(sx1r, sx1i)
                        sy1 = complex(sy1r, sy1i)
                        sx2 = complex(sx2r, sx2i)
                        sy2 = complex(sy2r, sy2i)
                        txy1 = complex(txy1r, txy1i)
                        txy2 = complex(txy2r, txy2i)

                    self.obj.add_new_eid(etype, dt, eid, gridC, fd1, sx1, sy1, txy1)
                    self.obj.add(dt, eid, gridC, fd2, sx2, sy2, txy2)

                    for node_id in xrange(nnodes):  # nodes pts
                        edata = data[n:n+60]  # 4*15=60
                        n += 60
                        out = s2.unpack(edata)
                        if self.debug4():
                            self.binary_debug.write('%s\n' % (str(out)))
                        (grid, fd1, sx1r, sx1i, sy1r, sy1i, txy1r, txy1i,
                               fd2, sx2r, sx2i, sy2r, sy2i, txy2r, txy2i) = out

                        if is_magnitude_phase:
                            sx1 = polar_to_real_imag(sx1r, sx1i)
                            sx2 = polar_to_real_imag(sx2r, sx2i)
                            sy1 = polar_to_real_imag(sy1r, sy1i)
                            sy2 = polar_to_real_imag(sy2r, sy2i)
                            txy1 = polar_to_real_imag(txy1r, txy1i)
                            txy2 = polar_to_real_imag(txy2r, txy2i)
                        else:
                            sx1 = complex(sx1r, sx1i)
                            sx2 = complex(sx2r, sx2i)
                            sy1 = complex(sy1r, sy1i)
                            sy2 = complex(sy2r, sy2i)
                            txy1 = complex(txy1r, txy1i)
                            txy2 = complex(txy2r, txy2i)

                        self.obj.addNewNode(dt, eid, grid, fd1, sx1, sy1, txy1)
                        self.obj.add(dt, eid, grid, fd2, sx2, sy2, txy2)
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [88, 90]: # nonlinear shells
            # 88-CTRIA3NL
            # 90-CQUAD4NL
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 13:  # real
                if self.isStress():
                    self.create_transient_object(self.nonlinearPlateStress, NonlinearQuad)
                else:
                    self.create_transient_object(self.nonlinearPlateStrain, NonlinearQuad)

                ntotal = 52  # 4*13
                s = Struct(b'i12f')  # 1+12=13
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)
                    if self.debug4():
                        self.binary_debug.write('CQUADNL-90 - %s\n' % str(out))

                    (eid_device, fd1, sx1, sy1, sz1, txy1, es1, eps1, ecs1,
                                      ex1, ey1, ez1, exy1) = out
                    eid = (eid_device - self.device_code) // 10
                    indata = (eid, fd1, sx1, sy1, sz1, txy1, es1, eps1, ecs1,
                                        ex1, ey1, ez1, exy1)
                    self.obj.add_new_eid(self.element_type, dt, indata)
                    #print "eid=%s axial=%s equivStress=%s totalStrain=%s effPlasticCreepStrain=%s effCreepStrain=%s linearTorsionalStresss=%s" % (
                        #eid, axial, equivStress, totalStrain, effPlasticCreepStrain, effCreepStrain, linearTorsionalStresss)
                    n += ntotal
            elif self.format_code == 1 and self.num_wide == 25:  # TODO: real?
                if self.isStress():
                    self.create_transient_object(self.nonlinearPlateStress, NonlinearQuad)
                else:
                    self.create_transient_object(self.nonlinearPlateStrain, NonlinearQuad)

                ntotal = 100  # 4*25
                s = Struct(b'i24f') # 1+24=25
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)
                    if self.debug4():
                        self.binary_debug.write('CQUADNL-90 - %s\n' % str(out))
                    (eid_device, fd1, sx1, sy1, undef1, txy1, es1, eps1, ecs1, ex1, ey1, undef2, etxy1,
                                 fd2, sx2, sy2, undef3, txy2, es2, eps2, ecs2, ex2, ey2, undef4, etxy2) = out
                    eid = (eid_device - self.device_code) // 10
                    #in_data = (eid, fd1, sx1, sy1, txy1, es1, eps1, ecs1, ex1, ey1, etxy1,
                                    #fd2, sx2, sy2, txy2, es2, eps2, ecs2, ex2, ey2, etxy2)
                    self.obj.add_new_eid(self.element_type, dt, (eid,
                                                                 fd1, sx1, sy1, undef1, txy1, es1, eps1, ecs1, ex1, ey1, undef2, etxy1))
                    self.obj.add(dt, (eid,
                                      fd2, sx2, sy2, undef3, txy2, es2, eps2, ecs2, ex2, ey2, undef4, etxy2))
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [95, 96, 97, 98]: # composite shell
            # 95 - CQUAD4
            # 96 - CQUAD8
            # 97 - CTRIA3
            # 98 - CTRIA6 (composite)
            if self.isStress():
                result_name = 'compositePlateStress'
                slot = self.compositePlateStress

                ComplexCompositePlateStress = None
                obj_real = RealCompositePlateStress
                obj_complex = ComplexCompositePlateStress

                #result_vector_name
                ComplexCompositePlateStressVector = None
                obj_vector_real = RealCompositePlateStressVector
                obj_vector_complex = ComplexCompositePlateStressVector
                if self.element_type == 95: # CQUAD4
                    result_vector_name = 'cquad4_composite_stress'
                    slot_vector = self.cquad4_composite_stress
                elif self.element_type == 96:  # CQUAD8
                    result_vector_name = 'cquad8_composite_stress'
                    slot_vector = self.cquad8_composite_stress
                elif self.element_type == 97:  # CTRIA3
                    result_vector_name = 'ctria3_composite_stress'
                    slot_vector = self.ctria3_composite_stress
                elif self.element_type == 98:  # CTRIA6
                    result_vector_name = 'ctria6_composite_stress'
                    slot_vector = self.ctria6_composite_stress

                    #result_vector_name = 'ctriar_composite_stress'
                    #slot_vector = self.ctriar_composite_stress
                #elif self.element_type == 10:  # CTRIA6
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)
            else:
                result_name = 'compositePlateStrain'
                slot = self.compositePlateStrain

                ComplexCompositePlateStrain = None
                obj_real = RealCompositePlateStrain
                obj_complex = ComplexCompositePlateStrain

                #result_vector_name
                ComplexCompositePlateStrainVector = None
                obj_vector_real = RealCompositePlateStrainVector
                obj_vector_complex = ComplexCompositePlateStrainVector
                if self.element_type == 95: # CQUAD4
                    result_vector_name = 'cquad4_composite_strain'
                    slot_vector = self.cquad4_composite_strain
                elif self.element_type == 96:  # CQUAD8
                    result_vector_name = 'cquad8_composite_strain'
                    slot_vector = self.cquad8_composite_strain
                elif self.element_type == 97:  # CTRIA3
                    result_vector_name = 'ctria3_composite_strain'
                    slot_vector = self.ctria3_composite_strain
                elif self.element_type == 98:  # CTRIA6
                    result_vector_name = 'ctria6_composite_strain'
                    slot_vector = self.ctria6_composite_strain
                else:
                    msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
                    return self._not_implemented_or_skip(data, msg)

            etype = self.element_name
            if self.format_code == 1 and self.num_wide == 11:  # real
                ntotal = 44
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_real, obj_vector_real)
                if auto_return:
                    return nelements * self.num_wide * 4

                s = Struct(b'ii9f')
                if self.debug:
                    self.binary_debug.write('  [cap, element1, element2, ..., cap]\n')
                    self.binary_debug.write('  cap = %i  # assume 1 cap when there could have been multiple\n' % len(data))
                    self.binary_debug.write('  element1 = [eid_device, layer, o1, o2, t12, t1z, t2z, angle, major, minor, ovm)]\n')
                    self.binary_debug.write('  nelements=%i; nnodes=1 # centroid\n' % nelements)

                eid_old = 0
                if hasattr(self, 'eid_old'):
                    eid_old = self.eid_old

                for i in xrange(nelements):
                    #if i % 10000 == 0:
                        #print 'i = ', i
                    edata = data[n:n+44]  # 4*11
                    out = s.unpack(edata)
                    (eid_device, layer, o1, o2, t12, t1z, t2z, angle, major, minor, ovm) = out
                    eid = (eid_device - self.device_code) // 10

                    if self.debug4():
                        self.binary_debug.write('  eid=%i; layer=%i; C=[%s]\n' % (eid, layer, ', '.join(['%r' % di for di in out])))

                    if eid != eid_old:  # originally initialized to None, the buffer doesnt reset it, so it is the old value
                        #print "1 - eid=%s layer=%i o1=%i o2=%i ovm=%i" % (eid, layer, o1, o2, ovm)
                        self.obj.add_new_eid(etype, dt, eid, layer, o1, o2, t12, t1z, t2z, angle, major, minor, ovm)
                    else:
                        #print "2 - eid=%s layer=%i o1=%i o2=%i ovm=%i" % (eid, layer, o1, o2, ovm)
                        self.obj.add(dt, eid, layer, o1, o2, t12, t1z, t2z, angle, major, minor, ovm)
                    eid_old = eid
                    n += 44
                self.eid_old = eid_old
            elif self.format_code in [2, 3] and self.num_wide == 9:  # TODO: imag? - not done...
                msg = 'num_wide=%s' % self.num_wide
                nelements = len(data) // ntotal
                auto_return = self._create_oes_object2(nelements,
                                                       result_name, result_vector_name,
                                                       slot, slot_vector,
                                                       obj_complex, obj_vector_complex)
                if auto_return:
                    return nelements * self.num_wide * 4
                return self._not_implemented_or_skip(data, msg)

                if self.isStress():
                    #self.create_transient_object(self.compositePlateStress, ComplexCompositePlateStress)  # undefined
                    raise NotImplementedError('ComplexCompositePlateStrain')
                else:
                    #self.create_transient_object(self.compositePlateStrain, ComplexCompositePlateStrain)  # undefined
                    raise NotImplementedError('ComplexCompositePlateStrain')
                # TODO: this is an OEF result???
                #    furthermore the actual table is calle dout as
                #    'i8si4f4s', not 'i8si3fi4s'
                ntotal = 36
                nelements = len(data) // ntotal
                s = Struct(b'i')
                s2 = Struct(b'8si3fi4s')
                s3 = Struct(b'8si4f4s')
                for i in xrange(nelements):
                    #out = s.unpack(data[n:n + ntotal])
                    eid_device, = s.unpack(data[n:n+4])
                    #t, = s.unpack(data[n:n+4])
                    #eid = (eid_device - self.device_code) // 10

                    if eid_device > 0:
                        #print ""
                        #print "eid =", eid_device
                        #print "t =", t
                        out = s2.unpack(data[n+4:n+ntotal])
                    else:
                        out1 = s2.unpack(data[n+4:n+ntotal])
                        out = s3.unpack(data[n+4:n+ntotal])
                        #print(out1)
                    #print(out)
                    (theory, lamid, fp, fm, fb, fmax, fflag) = out

                    if self.debug4():
                        self.binary_debug.write('%s-%s - (%s) + %s\n' % (self.element_name, self.element_type, eid_device, str(out)))
                    #print "eid=%s loc=%s rs=%s azs=%s as=%s ss=%s maxp=%s tmx=%s octs=%s" % (eid,loc,rs,azs,As,ss,maxp,tmax,octs)
                    self.obj.add_new_eid(dt, eid, theory, lamid, fp, fm, fb, fmax, fflag)
                    n += ntotal
                raise NotImplementedError('this is a really weird case...')
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        #=========================
        elif self.element_type in [53]: # axial plates - ctriax6
            # 53 - CTRIAX6
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 33: # real
                if self.isStress():
                    self.create_transient_object(self.ctriaxStress, RealTriaxStress)
                else:
                    self.create_transient_object(self.ctriaxStrain, RealTriaxStrain)

                ntotal = 132  # (1+8*4)*4 = 33*4 = 132
                nelements = len(data) // ntotal

                s1 = Struct(b'2i7f')  # 36
                s2 = Struct(b'i7f')
                for i in xrange(nelements):
                    out = s1.unpack(data[n:n + 36])
                    (eid_device, loc, rs, azs, As, ss, maxp, tmax, octs) = out
                    if self.debug4():
                        self.binary_debug.write('CTRIAX6-53A - %s\n' % (str(out)))
                    eid = (eid_device - self.device_code) // 10
                    #print "eid=%s loc=%s rs=%s azs=%s as=%s ss=%s maxp=%s tmx=%s octs=%s" % (eid,loc,rs,azs,As,ss,maxp,tmax,octs)
                    self.obj.add_new_eid(dt, eid, loc, rs, azs, As, ss, maxp, tmax, octs)
                    n += 36
                    for i in xrange(3):
                        out = s2.unpack(data[n:n + 32])
                        (loc, rs, azs, As, ss, maxp, tmax, octs) = out
                        if self.debug4():
                            self.binary_debug.write('CTRIAX6-53B - %s\n' % (str(out)))
                        #print "eid=%s loc=%s rs=%s azs=%s as=%s ss=%s maxp=%s tmx=%s octs=%s" % (eid,loc,rs,azs,As,ss,maxp,tmax,octs)
                        self.obj.add(dt, eid, loc, rs, azs, As, ss, maxp, tmax, octs)
                        n += 32  # 4*8
            elif self.format_code in [2, 3] and self.num_wide == 37: # imag
                msg = 'num_wide=%s' % self.num_wide
                #return self._not_implemented_or_skip(data, msg)

                #if self.isStress():
                    #self.create_transient_object(self.ctriaxStress, ComplexTriaxStress)  # undefined
                    #raise NotImplementedError('ComplexTriaxStress')
                #else:
                    #self.create_transient_object(self.ctriaxStrain, ComplexTriaxStrain)  # undefined
                    #raise NotImplementedError('ComplexTriaxStrain')
                s1 = Struct(b'ii8f')
                s2 = Struct(b'i8f')

                num_wide = 1 + 4 * 9
                ntotal = num_wide * 4
                assert num_wide == self.num_wide, num_wide
                nelements = len(data) // ntotal  # (1+8*4)*4 = 33*4 = 132

                for i in xrange(nelements):
                    out = s1.unpack(data[n:n + 40])
                    (eid_device, loc, rsr, rsi, azsr, azsi, Asr, Asi, ssr, ssi) = out
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('CTRIAX6-53 eid=%i\n    %s\n' % (eid, str(out)))

                    if is_magnitude_phase:
                        rs = polar_to_real_imag(rsr, rsi)
                        azs = polar_to_real_imag(azsr, azsi)
                        As = polar_to_real_imag(Asr, Asi)
                        ss = polar_to_real_imag(ssr, ssi)
                    else:
                        rs = complex(rsr, rsi)
                        azs = complex(azsr, azsi)
                        As = complex(Asr, Asi)
                        ss = complex(ssr, ssi)
                    #self.obj.add_new_eid(dt, eid, loc, rs, azs, As, ss)

                    n += 40
                    for i in xrange(3):
                        out = s2.unpack(data[n:n + 36])
                        (loc, rsr, rsi, azsr, azsi, Asr, Asi, ssr, ssi) = out
                        if self.debug4():
                            self.binary_debug.write('    %s\n' % (str(out)))
                        #print "eid=%s loc=%s rs=%s azs=%s as=%s ss=%s" % (eid,loc,rs,azs,As,ss)

                        if is_magnitude_phase:
                            rs = polar_to_real_imag(rsr, rsi)
                            azs = polar_to_real_imag(azsr, azsi)
                            As = polar_to_real_imag(Asr, Asi)
                            ss = polar_to_real_imag(ssr, ssi)
                        else:
                            rs = complex(rsr, rsi)
                            azs = complex(azsr, azsi)
                            As = complex(Asr, Asi)
                            ss = complex(ssr, ssi)
                        #self.obj.add(dt, eid, loc, rs, azs, As, ss)
                        n += 36  # 4*8
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)
        elif self.element_type in [102]: # bush
            # 102-CBUSH
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 7:  # real
                if self.isStress():
                    self.create_transient_object(self.bushStress, BushStress)
                else:
                    self.create_transient_object(self.bushStrain, BushStrain)
                assert self.num_wide == 7, "num_wide=%s not 7" % self.num_wide
                ntotal = 28  # 4*7

                nelements = len(data) // ntotal
                s = Struct(b'i6f')
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)  # num_wide=7
                    if self.debug4():
                        self.binary_debug.write('CBUSH-102 - %s\n' % str(out))

                    (eid_device, tx, ty, tz, rx, ry, rz) = out
                    eid = (eid_device - self.device_code) // 10

                    self.obj.add_new_eid(self.element_type, dt, eid, tx, ty, tz, rx, ry, rz)
                    n += ntotal
            elif self.format_code in [2, 3] and self.num_wide == 13:  # imag
                if self.isStress():
                    self.create_transient_object(self.bushStress, ComplexBushStress)
                else:
                    self.create_transient_object(self.bushStrain, ComplexBushStrain)
                ntotal = 52  # 4*13

                nelements = len(data) // ntotal
                s = Struct(b'i12f')
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)  # num_wide=7
                    if self.debug4():
                        self.binary_debug.write('CBUSH-102 - %s\n' % str(out))

                    (eid_device, txr, tyr, tzr, rxr, ryr, rzr,
                                 txi, tyi, tzi, rxi, ryi, rzi) = out
                    eid = (eid_device - self.device_code) // 10

                    if is_magnitude_phase:
                        tx = polar_to_real_imag(txr, txi)
                        ty = polar_to_real_imag(tyr, tyi)
                        tz = polar_to_real_imag(tzr, tzi)
                        rx = polar_to_real_imag(rxr, rxi)
                        ry = polar_to_real_imag(ryr, ryi)
                        rz = polar_to_real_imag(rzr, rzi)
                    else:
                        tx = complex(txr, txi)
                        ty = complex(tyr, tyi)
                        tz = complex(tzr, tzi)
                        rx = complex(rxr, rxi)
                        ry = complex(ryr, ryi)
                        rz = complex(rzr, rzi)
                    self.obj.add_new_eid(self.element_type, dt, eid, tx, ty, tz, rx, ry, rz)
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [40]:  # bush
            # 40-CBUSH1D
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 8:  # real
                if self.isStress():
                    self.create_transient_object(self.bush1dStressStrain, RealBush1DStress)  # undefined
                else:
                    #self.create_transient_object(self.bush1dStressStrain, Bush1DStrainObject)  # undefined
                    raise NotImplementedError('self.bush1dStressStrain; numwide=8')

                ntotal = 32  # 4*8
                s = Struct(b'i6fi')
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]
                    out = s.unpack(edata)  # num_wide=25
                    if self.debug4():
                        self.binary_debug.write('CBUSH1D-40 - %s\n' % (str(out)))
                    (eid_device, fe, ue, ve, ao, ae, ep, fail) = out
                    eid = (eid_device - self.device_code) // 10

                    # axial_force, axial_displacement, axial_velocity, axial_stress, axial_strain, plastic_strain, is_failed
                    self.obj.add_new_eid(self.element_type, dt, eid, fe, ue, ve, ao, ae, ep, fail)
                    n += ntotal
            elif self.format_code in [2, 3] and self.num_wide == 9:  # imag
                if self.isStress():
                    self.create_transient_object(self.bush1dStressStrain, ComplexBush1DStress)  # undefined
                else:
                    #self.create_transient_object(self.bush1dStressStrain, ComplexBush1DStress)  # undefined
                    raise NotImplementedError('self.bush1dStressStrain; complex strain')

                ntotal = 36  # 4*9
                s = Struct(b'i8f')
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]

                    out = s.unpack(edata)  # num_wide=25
                    (eid_device, fer, uer, aor, aer,
                                 fei, uei, aoi, aei) = out
                    eid = (eid_device - self.device_code) // 10

                    if is_magnitude_phase:
                        fe = polar_to_real_imag(fer, fei)
                        ue = polar_to_real_imag(uer, uei)
                        ao = polar_to_real_imag(aor, aoi)
                        ae = polar_to_real_imag(aer, aei)
                    else:
                        fe = complex(fer, fei)
                        ue = complex(uer, uei)
                        ao = complex(aor, aoi)
                        ae = complex(aer, aei)
                    self.obj.add_new_eid(self.element_type, dt, eid, fe, ue, ao, ae)
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)


        elif self.element_type in [87, 89, 92]:  # nonlinear rods
            # 87-CTUBENL
            # 89-RODNL
            # 92-CONRODNL
            if self.read_mode == 1:
                return len(data)

            slot = self.nonlinearRodStress if self.isStress() else self.nonlinearRodStrain
            if self.element_type == 87:
                name = 'CTUBENL-87'
            elif self.element_type == 89:
                name = 'RODNL-89'
            elif self.element_type == 92:
                name = 'CONRODNL-92'
            else:
                msg = 'element_type=%s' % self.element_type
                return self._not_implemented_or_skip(data, msg)

            if self.format_code == 1 and self.num_wide == 7:  # real
                self.create_transient_object(slot, NonlinearRod)
                s = Struct(b'i6f')  # 1+6=7
                ntotal = 28  #  7*4 = 28
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]
                    out = s.unpack(edata)

                    (eid_device, axial, equivStress, totalStrain, effPlasticCreepStrain,
                        effCreepStrain, linearTorsionalStresss) = out
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('CRODNL-%s - %s\n' % (name, str(out)))
                    indata = (eid, axial, equivStress, totalStrain, effPlasticCreepStrain, effCreepStrain, linearTorsionalStresss)
                    #print "eid=%s axial=%s equivStress=%s totalStrain=%s effPlasticCreepStrain=%s effCreepStrain=%s linearTorsionalStresss=%s" % (eid,axial,equivStress,totalStrain,effPlasticCreepStrain,effCreepStrain,linearTorsionalStresss)
                    self.obj.add(self.element_type, dt, indata)
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [224, 225]: # nonlinear spring
            # 224-CELAS1
            # 225-CELAS3
            # nonlinearSpringStress
            numwide_real = 3
            if self.read_mode == 1:
                return len(data)
            if self.num_wide == numwide_real:
                if self.isStress():
                    self.create_transient_object(self.nonlinearSpringStress, NonlinearSpringStress)
                else:
                    #self.create_transient_object(self.nonlinearSpringStrain, NonlinearSpringStrainObject)  # undefined
                    raise NotImplementedError('NonlinearSpringStrainObject')

                assert self.num_wide == 3, "num_wide=%s not 3" % self.num_wide
                ntotal = 12  # 4*3
                nelements = len(data) // ntotal
                s = Struct(b'i2f')
                for i in xrange(nelements):
                    edata = data[n:n+ntotal]
                    out = s.unpack(edata)  # num_wide=3
                    (eid_device, force, stress) = out
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('%s-%s - %s\n' % (self.element_name, self.element_type, str(out)))
                    self.obj.add_new_eid(self.element_name, dt, eid, force, stress)
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [35]:
            # 35-CON
            return len(data)
        elif self.element_type in [60, 61]:
            # 60-DUM8
            # 61-DUM9
            return len(data)
        elif self.element_type in [69]:  # cbend
            # 69-CBEND
            return len(data)
        elif self.element_type in [86]:  # cgap
            # 86-GAPNL
            if self.read_mode == 1:
                return len(data)
            if self.format_code == 1 and self.num_wide == 11:  # real?
                if self.isStress():
                    self.create_transient_object(self.nonlinearGapStress, NonlinearGapStressObject)
                else:
                    #self.create_transient_object(self.nonlinearGapStrain, NonlinearGapStrainObject)  # undefined
                    raise NotImplementedError('NonlinearGapStrainObject')
                ntotal = 44  # 4*11
                s = Struct(b'i8f4s4s')
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n + ntotal]

                    out = s.unpack(edata)  # num_wide=25
                    (eid_device, cpx, shy, shz, au, shv, shw, slv, slp, form1, form2) = out
                    eid = (eid_device - self.device_code) // 10
                    if self.debug4():
                        self.binary_debug.write('CGAPNL-86 - %s\n' % str(out))
                    self.obj.add_new_eid(dt, eid, cpx, shy, shz, au, shv, shw, slv, slp, form1, form2)
                    n += ntotal
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

            return len(data)
        elif self.element_type in [94]:
            # 94-BEAMNL
            return len(data)
        elif self.element_type in [85, 91, 93]:
            # 85-TETRANL
            # 91-PENTANL
            # 93-HEXANL
            #raise NotImplementedError('element_type=%s element_name=%s ntotal not defined...' % (self.element_type, self.element_name))

            #85: 2 + (18 - 2) * 5,  # Nonlinear CTETRA
            #91: 4 + (25 - 4) * 7,  # Nonlinear CPENTA
            #93: 4 + (25 - 4) * 9,  # Nonlinear CHEXA
            if self.element_type == 85:
                etype = 'CTETRANL'
                nnodes = 5
            elif self.element_type == 91:
                etype = 'CPENTANL'
                nnodes = 7
            elif self.element_type == 93:
                etype = 'CHEXANL'
                nnodes = 9
            else:
                msg = 'element_type=%s' % self.element_type
                return self._not_implemented_or_skip(data, msg)

            numwide_real = 4 + (25 - 4) * nnodes  # real???
            numwide_random = 2 + (18 - 2) * nnodes  # imag???
            #print "numwide=%s numwide_real=%s numwide_imag=%s" % (self.num_wide, numwide_real, numwide_imag)

            #numwide_real = 0
            #numwide_imag = 2 + 16 * nnodes
            #ntotal = 8 + 64 * nnodes

            if self.format_code == 1 and self.num_wide == numwide_real:
                ntotal = numwide_real * 4
                #if self.isStress():
                    #self.create_transient_object(self.nonlinearPlateStress, NonlinearSolid)
                #else:
                    #self.create_transient_object(self.nonlinearPlateStrain, NonlinearSolid)
                #self.handle_results_buffer(self.OES_CQUAD4NL_90, resultName, name)
            elif self.format_code == 1 and self.num_wide == numwide_random:  # random
            #elif self.format_code in [2, 3] and self.num_wide == numwide_imag:  # imag
                ntotal = numwide_random * 4
                #if self.isStress():
                    #self.create_transient_object(self.nonlinearPlateStress, NonlinearSolid)
                #else:
                    #self.create_transient_object(self.nonlinearPlateStrain, NonlinearSolid)

                n = 0
                s1 = Struct(b'i4s')
                s2 = Struct(b'i15f')
                nelements = len(data) // ntotal
                for i in xrange(nelements):  # 2+16*9 = 146 -> 146*4 = 584
                    edata = data[n:n+8]
                    n += 8

                    out = s1.unpack(edata)
                    if self.debug4():
                        self.binary_debug.write('%s-%s - %s\n' % (etype, self.element_type, str(out)))
                    (eid_device, cType) = out
                    eid = (eid_device - self.device_code) // 10

                    for i in xrange(nnodes):
                        edata = data[n:n+64]
                        n += 64
                        out = s2.unpack(edata)
                        if self.debug4():
                            self.binary_debug.write('%s-%sB - %s\n' % (etype, self.element_type, str(out)))

                        assert len(out) == 16
                        (grid, sx, sy, sz, sxy, syz, sxz, se, eps,
                          ecs, ex, ey, ez, exy, eyz, exz) = out
                        #print "eid=%3s cType=%s sx=%i sy=%i sz=%i sxy=%s syz=%i szx=%i se=%s" % (eid,cType,sx,sy,sz,sxy,syz,sxz,se)
                        #print "gid=%3s ecs=%.3g   ex=%.3g ey=%.3g ez=%.3g exy=%.3g eyz=%.3g ezx=%.3g"  % (grid,ecs,ex,ey,ez,exy,eyz,exz)
                        #assert cType == 'GRID',cType
                        #print("cType =", cType)
            else:
                msg = 'num_wide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [100]:  # bars
            # 100-BARS
            return len(data)
        elif self.element_type in [101]:
            # 101-AABSF
            return len(data)
        elif self.element_type in [140, 201]:
            # 140-HEXA8FD, 201-QUAD4FD
            return len(data)
        elif self.element_type in [145, 146, 147]:
            # 145-VUHEXA  (8 nodes)
            # 146-VUPENTA (6 nodes)
            # 147-VUTETRA (4 nodes)
            if self.element_type == 147:
                etype = 'VUTETRA'
                nnodes = 4
                #numwideA = 2 + (14 - 2) * nnodes  # 50
                #numwideB = 2 + (9 - 2) * nnodes  # 30
                #numwideC = 2 + 13 * nnodes  # 54
            elif self.element_type == 146:
                etype = 'VUPENTA'
                nnodes = 6
            elif self.element_type == 145:
                etype = 'VUHEXA'
                nnodes = 8
            else:
                msg = 'element_type=%s' % self.element_type
                return self._not_implemented_or_skip(data, msg)

            #num_wideA = 2 + 12 * nnodes
            #ntotal = 8 + 48 * nnodes
            # assuming TETRA...
            numwideA = 2 + (14 - 2) * nnodes  # 50
            numwideB = 2 + (9 - 2) * nnodes  # 30
            numwideC = 2 + 13 * nnodes  # 54
            if self.num_wide == numwideA:
                ntotal = numwideA * 4
                s1 = Struct(b'ii')
                s2 = Struct(b'i11f')
                nelements = len(data) // ntotal  # 2+16*9 = 146 -> 146*4 = 584
                for i in xrange(nelements):
                    edata = data[n:n+8]
                    (eid_device, parent_id) = s1.unpack(edata)
                    eid = (eid_device - self.device_code) // 10

                    for i in xrange(nnodes):
                        edata = data[n:n+48]
                        out = s2.unpack(edata)
                        if self.debug4():
                            self.binary_debug.write('%s-%s - %s\n' % (etype, self.element_type, str(out)))
                        assert len(out) == 12
                        (grid, xnorm, ynorm, znorm, txy, tyz, txz,
                         prin1, prin2, prin3, smean, vonoRoct) = out
                        #print "eid=%3s cType=%s sx=%i sy=%i sz=%i sxy=%s syz=%i szx=%i se=%s" % (eid,cType,sx,sy,sz,sxy,syz,sxz,se)
                        #print "gid=%3s ecs=%.3g   ex=%.3g ey=%.3g ez=%.3g exy=%.3g eyz=%.3g ezx=%.3g"  % (grid,ecs,ex,ey,ez,exy,eyz,exz)
                        #assert cType == 'GRID',cType
                        #print("grid =",grid)
                return len(data)
            elif self.num_wide == numwideB:
                ntotal = numwideC * 4
                nelements = len(data) // ntotal
                n = nelements * ntotal
            elif self.num_wide == numwideC:
                ntotal = numwideC * 4
                nelements = len(data) // ntotal
                n = nelements * ntotal
            else:
                msg = 'numwide=%s A=%s B=%s C=%s' % (self.num_wide, numwideA, numwideB, numwideC)
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [139]:
            # 139-QUAD4FD
            if self.read_mode == 1:
                return len(data)
            if self.num_wide == 30:
                if self.isStress():
                    self.create_transient_object(self.hyperelasticPlateStrain, HyperelasticQuad)
                else:
                    msg = 'HyperelasticQuadObject???'
                    return self._not_implemented_or_skip(data, msg)

                n = 0
                ntotal = 120  # 36+28*3
                s1 = Struct(b'i4si6f')  # 1 + 4+1+6 = 12
                s2 = Struct(b'i6f')
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    edata = data[n:n+36]  # 4*9
                    out = s1.unpack(edata)
                    if self.debug4():
                        self.binary_debug.write('CQUAD4FD-139A- %s\n' % (str(out)))

                    (eid_device, Type, ID, sx, sy, sxy, angle, smj, smi) = out
                    eid = (eid_device - self.device_code) // 10
                    self.obj.add_new_eid(dt, [eid, Type, sx, sy, sxy, angle, smj, smi])
                    #print "eid=%s Type=%s\n***ID=%s sx=%s sy=%s sxy=%s angle=%s major=%s minor=%s" % (eid, Type, ID, sx, sy, sxy,
                    #                                                                                  angle, smj, smi)
                    n += 36

                    for i in xrange(3):
                        edata = data[n:n + 28]  # 4*7
                        out = s2.unpack(edata)
                        if self.debug4():
                            self.binary_debug.write('               %s\n' % (str(out)))
                        (ID, sx, sy, sxy, angle, smj, smi) = out
                        self.obj.add(dt, eid, out)
                        #print "***ID=%s sx=%s sy=%s sxy=%s angle=%s major=%s minor=%s" % (ID, sx, sy, sxy, angle, smj, smi)
                        n += 28
            else:
                msg = 'numwide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)
        elif self.element_type in [189]:
            # 189-VUQUAD
            if self.element_type == 189:  # VQUAD
                #ntotal = 440  # 6+(33-7)*4 =  -> 110*4 = 440
                nnodes = 4    # 4 corner points + 1 centroid
                etype = 'VUQUAD4'
            #elif self.element_type == 144:  # CQUAD4
                #ntotal = 440  # 6+(33-7)*4 =  -> 110*4 = 440
                #nnodes = 4    # 4 corner points
                #etype = 'CQUAD4'
            #elif self.element_type == 64:  # CQUAD8
                #ntotal = 348  # 2+17*5 = 87 -> 87*4 = 348
                #nnodes = 4    # centroid + 4 corner points
                #eType = 'CQUAD8'
            #elif self.element_type == 82:  # CQUADR
                #ntotal = 348  # 2+17*5 = 87 -> 87*4 = 348
                #nnodes = 4    # centroid + 4 corner points
                #eType = 'CQUAD4'  # TODO write the word CQUADR
            #elif self.element_type == 75:  # CTRIA6
                #ntotal = 280  # 2+17*3 = 70 -> 70*4 = 280
                #nnodes = 3    # centroid + 3 corner points
                #eType = 'CTRIA6'
            #elif self.element_type == 70:  # CTRIAR
                #ntotal = 280  # 2+17*3 = 70 -> 70*4 = 280
                #nnodes = 3    # centroid + 3 corner points
                #eType = 'CTRIAR'  # TODO write the word CTRIAR
            else:
                msg = 'element_type=%s not defined...' % self.element_type
                return self._not_implemented_or_skip(data, msg)

            numwide_real = 6 + (23 - 6) * nnodes  # real???
            numwide_imag = 6 + (33 - 6) * nnodes  # imag???

            if self.format_code == 1 and self.num_wide == numwide_real:  # real???
                ntotal = numwide_real * 4
                s2 = Struct(b'3i4s2i')
                s3 = Struct(b'i16f')
                nelements = len(data) // ntotal
                for i in xrange(nelements):
                    (eid_device, parent, coord, icord, theta, itype) = s2.unpack(data[n:n+24])
                    n += 24
                    eid = (eid_device - self.device_code) // 10
                    assert eid > 0, eid
                    edata = data[n:n+68]
                    out = s3.unpack(edata)  # len=17*4
                    n += 68

                    if self.debug4():
                        self.binary_debug.write('%s-%s - %s\n' % (etype, self.element_type, str(out)))

                    #self.obj.addNewNode(dt, eid, parent, coord, icord, theta, itype)
                    #self.obj.add_new_eid(eType, dt, eid, parent, coord, icord, theta, itype)
                    for node_id in xrange(nnodes-1):  # nodes pts
                        edata = data[n:n+68]
                        n += 68
                        out = s3.unpack(edata)
                        if self.debug4():
                            self.binary_debug.write('              %s\n' % (str(out)))

                        (vuid, dummy, dummy2, msx, msy, mxy, dummy3, dummy4, dummy5,
                         bcx, bcy, bcxy, tyz, tzx, dummy6, dummy7, dummy8) = out
                        #self.obj.add(vuid, dummy, dummy2, msx, msy, mxy,
                                     #dummy3, dummy4, dummy5,
                                     #bcx, bcy, bcxy, tyz, tzx,
                                     #dummy6, dummy7, dummy8)
            elif self.num_wide == numwide_imag:
                ntotal = numwide_imag * 4
                nelements = len(data) // ntotal
                n = nelements * ntotal
            else:
                msg = 'numwide=%s' % self.num_wide
                return self._not_implemented_or_skip(data, msg)

        elif self.element_type in [47, 48, 189, 190]:
            # 47-AXIF2
            # 48-AXIF3
            # 190-VUTRIA
            return len(data)
        elif self.element_type in [191]:
            # 191-VUBEAM
            return len(data)
        elif self.element_type in [50, 51, 203]:
            # 203-SLIF1D?
            # 50-SLOT3
            # 51-SLOT4
            return len(data)
        elif self.element_type in [160, 161, 162, 163, 164, 165, 166, 167, 168,
                                   169, 170, 171, 172, 202,
                                   204, 218, 211, 213, 214,
                                   216, 217, 219, 220, 221, 222, 223,
                                   226, 232, 233, 235]:
            # 160-PENTA6FD
            # 161-TETRA4FD
            # 162-TRIA3FD
            # 163-HEXAFD
            # 164-QUADFD
            # 165-PENTAFD
            # 166-TETRAFD
            # 167-TRIAFD
            # 168-TRIAX3FD
            # 169-TRIAXFD
            # 170-QUADX4FD
            # 171-QUADXFD
            # 172-QUADRNL
            # 202-HEXA8FD
            # 204-PENTA6FD
            # 211-TRIAFD
            # 213-TRIAXFD
            # 214-QUADX4FD
            # 216-TETRA4FD
            # 217-TRIA3FD
            # 218-HEXAFD
            # 219-QUADFD
            # 220-PENTAFD
            # 221-TETRAFD
            # 223-QUADXFD
            # 222-TRIAX3FD
            # 226-BUSH
            # 232-QUADRLC
            # 233-TRIARLC
            # 235-CQUADR
            return len(data)
        else:
            msg = 'sort1 Type=%s num=%s' % (self.element_name, self.element_type)
            return self._not_implemented_or_skip(data, msg)

        assert len(data) > 0, len(data)
        assert nelements > 0, 'nelements=%r element_type=%s element_name=%r' % (nelements, self.element_type, self.element_name)
        #assert len(data) % ntotal == 0, '%s n=%s nwide=%s len=%s ntotal=%s' % (self.element_name, len(data) % ntotal, len(data) % self.num_wide, len(data), ntotal)
        assert self.num_wide * 4 == ntotal, 'numwide*4=%s ntotal=%s' % (self.num_wide*4, ntotal)
        assert self.thermal == 0, self.thermal
        assert n > 0, n
        return n

    def OESRT_CQUAD4_95(self, data):
        assert self.num_wide == 9, "num_wide=%s not 9" % self.num_wide
        ntotal = 36  # 4*9

        n = 0
        s = Struct(b'i8si3fi4s')
        nelements = len(data) // ntotal
        for i in xrange(nelements):
            eData = data[n:n + ntotal]
            out = s.unpack(eData)  # num_wide=9
            if self.debug4():
                self.binary_debug.write('CQUAD4-95 - %s\n' % str(out))
            #eid,failure, ply, failureIndexPly, failureIndexBonding, failureIndexMax, flag
            # 3,TSAIWU,1,8.5640,0.0,None
            #print('out', out)

            (eid, failure, ply, strengthRatioPly, failureIndexBonding, strengthRatioBonding, flag, flag2) = out
            strengthRatioPly
            #print("eid=%s failure=%r ply=%s failureIndexPly=%s  failureIndexBonding=%s strengthRatioBonding=%s flag=%s flag2=%s" % (eid, failure.strip(), ply, failureIndexPly, failureIndexBonding, strengthRatioBonding, flag, flag2))
            print("eid=%s strengthRatioPly=%g failureIndexBonding=%s strengthRatioBonding=%s" % (eid, strengthRatioPly, failureIndexBonding, strengthRatioBonding))
            #self.obj.add_new_eid(element_name, dt, eid, force, stress)
            n += ntotal

    def _create_oes_object2(self, nelements,
                            result_name, result_vector_name,
                            slot, slot_vector,
                            obj, obj_vector):
        """
        Creates the self.obj parameter based on if this is vectorized or not.
        :param self: the object pointer
        :param nelements: the number of elements to preallocate for vectorization
        :type nelements: integer
        :param result_name: unused
        :type result_name: string
        :param result_name_vector: unused
        :type result_name_vector: string
        :param slot: the self dictionary that will be filled with a
                     non-vectorized result
        :type slot: dictionary
        :param slot_vector: the self dictionary that will be filled with a
                            vectorized result
        :type slot: slot_vector
        :param obj: a pointer to the non-vectorized class
        :param obj_vector: a pointer to the vectorized class
        :returns auto_return: a flag indicating a return n should be called
        :type auto_return: bool
        Since that's confusing, let's say we have real CTETRA stress data.
        We're going to fill self.solidStress with the class
        RealSolidStressObject.  If it were vectorized, we'd fill
        self.ctetra_stress. with RealSolidStressVector.  So we call:

        auto_return = self._create_oes_object2(self, nelements,
                            'solidStress', 'ctetra_stress',
                            self.solidStress, self.ctetra_stress,
                            RealSolidStressObject, RealSolidStressVector)
        if auto_return:
            return nelements * ntotal
        """
        auto_return = False
        is_vectorized = False
        if self.is_vectorized:
            if obj_vector is not None:
                is_vectorized = True
                #print "***vectorized..."

        if is_vectorized:
            #print("vectorized...read_mode=%s...%s" % (self.read_mode, result_vector_name))
            if self.read_mode == 1:
                self.create_transient_object(slot_vector, obj_vector)
                #print "read_mode 1", self.obj.ntimes
                self.result_names.add(result_vector_name)
                #print('self.obj =', self.obj)
                self.obj.nelements += nelements
                auto_return = True
            elif self.read_mode == 2:
                self.code = self._get_code()
                #print "***code =", self.code
                self.obj = slot_vector[self.code]
                #self.obj.update_data_code(self.data_code)
                self.obj.build()

        else:  # not vectorized
            self.result_names.add(result_name)
            #print("not vectorized...read_mode=%s...%s" % (self.read_mode, result_name))
            if self.read_mode == 1:
                self.result_names.add(result_name)
                auto_return = True
            # pass = 0/2
            self.create_transient_object(slot, obj)
        return auto_return
