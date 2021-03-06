from pyNastran.op2.resultObjects.tableObject import RealTableVector, ComplexTableVector, RealTableObject, ComplexTableObject
from pyNastran.f06.f06_formatting import writeFloats13E, writeImagFloats13E


class RealMPCForcesVector(RealTableVector):
    def __init__(self, data_code, is_sort1, isubcase, dt):
        RealTableVector.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_f06(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        words = ['                               F O R C E S   O F   M U L T I - P O I N T   C O N S T R A I N T\n', ]
                 #' \n',
                 #'      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        #words += self.get_table_marker()
        if self.nonlinear_factor is not None:
            return self._write_f06_transient_block(words, header, pageStamp, page_num, f)
        return self._write_f06_block(words, header, pageStamp, page_num, f)


class ComplexMPCForcesVector(ComplexTableVector):
    def __init__(self, data_code, is_sort1, isubcase, dt):
        ComplexTableVector.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_f06(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        words = ['                         C O M P L E X   F O R C E S   O F   M U L T I   P O I N T   C O N S T R A I N T\n', ]
        return self._write_f06_transient_block(words, header, pageStamp, page_num, f, is_mag_phase)


class RealMPCForces(RealTableObject):

    def __init__(self, data_code, is_sort1, isubcase, dt):
        RealTableObject.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_f06(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, page_num, f, is_mag_phase=is_mag_phase)
        msg = header + ['                               F O R C E S   O F   M U L T I - P O I N T   C O N S T R A I N T\n',
                        ' \n',
                        '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            grid_type = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            (rx, ry, rz) = rotation
            vals = [dx, dy, dz, rx, ry, rz]
            (vals2, is_all_zeros) = writeFloats13E(vals)
            [dx, dy, dz, rx, ry, rz] = vals2
            msg.append('%14i %6s     %-13s  %-13s  %-13s  %-13s  %-13s  %s\n' % (nodeID, grid_type, dx, dy, dz, rx, ry, rz.rstrip()))

        msg.append(pageStamp % page_num)
        f.write(''.join(msg))
        return page_num

    def _write_f06_transient(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        words = ['                               F O R C E S   O F   M U L T I - P O I N T   C O N S T R A I N T\n',
                 ' \n',
                 '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        msg = []
        for dt, translations in sorted(self.translations.iteritems()):
            header[1] = ' %s = %10.4E\n' % (self.data_code['name'], dt)
            msg += header + words
            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                grid_type = self.gridTypes[nodeID]

                (dx, dy, dz) = translation
                (rx, ry, rz) = rotation
                vals = [dx, dy, dz, rx, ry, rz]
                (vals2, is_all_zeros) = writeFloats13E(vals)
                #if not is_all_zeros:
                [dx, dy, dz, rx, ry, rz] = vals2
                msg.append('%14i %6s     %-13s  %-13s  %-13s  %-13s  %-13s  %s\n' % (nodeID, grid_type, dx, dy, dz, rx, ry, rz.rstrip()))

            msg.append(pageStamp % page_num)
            f.write(''.join(msg))
            page_num += 1
        return page_num - 1


class ComplexMPCForces(ComplexTableObject):
    def __init__(self, data_code, is_sort1, isubcase, dt):
        ComplexTableObject.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_f06(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        assert f is not None
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, page_num, f, is_mag_phase)
        msg = header + ['                               F O R C E S   O F   M U L T I - P O I N T   C O N S T R A I N T\n',
                        ' \n',
                        '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        raise RuntimeError('is this valid...')
        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            grid_type = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            #dxr=dx.real; dyr=dy.real; dzr=dz.real;
            #dxi=dx.imag; dyi=dy.imag; dzi=dz.imag

            (rx, ry, rz) = rotation
            #rxr=rx.real; ryr=ry.real; rzr=rz.real
            #rxi=rx.imag; ryi=ry.imag; rzi=rz.imag

            #vals = [dxr,dyr,dzr,rxr,ryr,rzr,dxi,dyi,dzi,rxi,ryi,rzi]
            vals = list(translation) + list(rotation)
            (vals2, is_all_zeros) = writeFloats13E(vals)
            #if not is_all_zeros:
            [dx, dy, dz, rx, ry, rz] = vals2
            msg.append('%14i %6s     %-13s  %-13s  %-13s  %-13s  %-13s  %s\n' % (nodeID, grid_type, dx, dy, dz, rx, ry, rz))
        msg.append(pageStamp % page_num)
        f.write(''.join(msg))
        return page_num

    def _write_f06_transient(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        assert f is not None
        words = ['                         C O M P L E X   F O R C E S   O F   M U L T I   P O I N T   C O N S T R A I N T\n',
                 '                                                          (REAL/IMAGINARY)\n',
                 ' \n',
                 '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        msg = []
        for dt, translations in sorted(self.translations.iteritems()):
            header[1] = ' %s = %10.4E\n' % (self.data_code['name'], dt)
            msg += header + words
            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                grid_type = self.gridTypes[nodeID]

                (dx, dy, dz) = translation
                (rx, ry, rz) = rotation

                vals = [dx, dy, dz, rx, ry, rz]
                (vals2, is_all_zeros) = writeImagFloats13E(vals, is_mag_phase)
                #if not is_all_zeros:
                [v1r, v2r, v3r, v4r, v5r, v6r, v1i,
                    v2i, v3i, v4i, v5i, v6i] = vals2
                msg.append('0%13i %6s     %-13s  %-13s  %-13s  %-13s  %-13s  %s\n' % (nodeID, grid_type, v1r, v2r, v3r, v4r, v5r, v6r.rstrip()))
                msg.append(' %13i %6s     %-13s  %-13s  %-13s  %-13s  %-13s  %s\n' % (nodeID, grid_type, v1i, v2i, v3i, v4i, v5i, v6i.rstrip()))

            msg.append(pageStamp % page_num)
            f.write(''.join(msg))
            page_num += 1
        return page_num - 1
