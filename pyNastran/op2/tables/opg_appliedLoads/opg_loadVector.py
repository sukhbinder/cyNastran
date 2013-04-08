from pyNastran.op2.resultObjects.tableObject import TableObject, ComplexTableObject
from pyNastran.f06.f06_formatting import writeFloats13E


class LoadVectorObject(TableObject):  # table_code=2, sort_code=0, thermal=0
    def __init__(self, data_code, is_sort1, isubcase, dt=None):
        TableObject.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_matlab(self, isubcase, f=None, isMagPhase=False):
        name = 'loadVector'
        if self.nonlinear_factor is None:
            return self._write_matlab(name, isubcase, f)
        else:
            return self._write_matlab_transient(name, isubcase, f)

    def write_f06(self, header, pageStamp, pageNum=1, f=None, isMagPhase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, pageNum, f)

        msg = header + ['                                                     L O A D   V E C T O R\n',
                        ' \n',
                        '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            gridType = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            (rx, ry, rz) = rotation
            vals = [dx, dy, dz, rx, ry, rz]
            (vals2, isAllZeros) = writeFloats13E(vals)
            if not isAllZeros:
                [dx, dy, dz, rx, ry, rz] = vals2
                msg.append('%14i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, gridType, dx, dy, dz, rx, ry, rz.rstrip()))

        msg.append(pageStamp + str(pageNum) + '\n')
        if f is not None:
            f.write(''.join(msg))
            msg = ['']
        return (''.join(msg), pageNum)

    def _write_f06_transient(self, header, pageStamp, pageNum=1, f=None, isMagPhase=False):
        msg = []
        words = ['                                                     L O A D   V E C T O R\n',
                 ' \n',
                 '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']

        for dt, translations in sorted(self.translations.iteritems()):
            header[1] = ' %s = %10.4E\n' % (self.data_code['name'], dt)
            msg += header + words
            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                gridType = self.gridTypes[nodeID]

                (dx, dy, dz) = translation
                (rx, ry, rz) = rotation

                vals = [dx, dy, dz, rx, ry, rz]
                (vals2, isAllZeros) = writeFloats13E(vals)
                if not isAllZeros:
                    [dx, dy, dz, rx, ry, rz] = vals2
                    msg.append('%14i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, gridType, dx, dy, dz, rx, ry, rz.rstrip()))

            msg.append(pageStamp + str(pageNum) + '\n')
            if f is not None:
                f.write(''.join(msg))
                msg = ['']
            pageNum += 1
        return (''.join(msg), pageNum - 1)

    def __reprTransient__(self):
        msg = '---TRANSIENT LOAD VECTOR---\n'
        #msg += '%s = %g\n' %(self.data_code['name'],self.dt)
        msg += self.writeHeader()

        for dt, translations in sorted(self.translations.iteritems()):
            msg += '%s = %g\n' % (self.data_code['name'], dt)
            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                gridType = self.gridTypes[nodeID]
                (dx, dy, dz) = translation
                (rx, ry, rz) = rotation

                msg += '%-10i %8s ' % (nodeID, gridType)
                vals = [dx, dy, dz, rx, ry, rz]
                for val in vals:
                    if abs(val) < 1e-6:
                        msg += '%10s ' % (0)
                    else:
                        msg += '%10.3e ' % (val)
                msg += '\n'
        return msg

    def __repr__(self):
        if self.nonlinear_factor is not None:
            return self.__reprTransient__()

        msg = '---LOAD VECTOR---\n'
        msg += self.writeHeader()

        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            gridType = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            (rx, ry, rz) = rotation

            msg += '%-10i %-8s ' % (nodeID, gridType)
            vals = [dx, dy, dz, rx, ry, rz]
            for val in vals:
                if abs(val) < 1e-6:
                    msg += '%10s ' % (0)
                else:
                    msg += '%10.3e ' % (val)
            msg += '\n'
        return msg

    def __reprTransient__(self):
        return self._write_f06_transient(['', ''], 'PAGE ', 1)[0]


class ComplexLoadVectorObject(ComplexTableObject):  # table_code=11, approach_code=???
    def __init__(self, data_code, is_sort1, isubcase, dt):
        ComplexTableObject.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_matlab(self, isubcase, f=None, isMagPhase=False):
        name = 'loadVector'
        if self.nonlinear_factor is None:
            return self._write_matlab(name, isubcase, f, isMagPhase)
        else:
            return self._write_matlab_transient(name, isubcase, f, isMagPhase)

    def write_f06(self, header, pageStamp, pageNum=1, f=None, isMagPhase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, pageNum, f, isMagPhase)
        msg = header + ['                                               C O M P L E X   L O A D   V E C T O R\n',
                        '                                                          (REAL/IMAGINARY)\n',
                        ' \n',
                        '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            gridType = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            (rx, ry, rz) = rotation

            if isMagPhase:
                dxr = abs(dx)
                dxi = angle(dx, deg=True)
                dyr = abs(dy)
                dyi = angle(dy, deg=True)
                dzr = abs(dz)
                dzi = angle(dz, deg=True)

                rxr = abs(rx)
                rxi = angle(rx, deg=True)
                ryr = abs(ry)
                ryi = angle(ry, deg=True)
                rzr = abs(rz)
                rzi = angle(rz, deg=True)
            else:
                dxr = dx.real
                dyr = dy.real
                dzr = dz.real
                dxi = dx.imag
                dyi = dy.imag
                dzi = dz.imag

                rxr = rx.real
                ryr = ry.real
                rzr = rz.real
                rxi = rx.imag
                ryi = ry.imag
                rzi = rz.imag

            vals = [dxr, dyr, dzr, rxr, ryr, rzr, dxi, dyi, dzi, rxi, ryi, rzi]
            (vals2, isAllZeros) = writeFloats13E(vals)
            [dxr, dyr, dzr, rxr, ryr, rzr,
             dxi, dyi, dzi, rxi, ryi, rzi] = vals2
            msg.append('0 %12i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, gridType, dxr, dyr, dzr, rxr, ryr, rzr.rstrip()))
            msg.append('  %12s %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % ('', '',           dxi, dyi, dzi, rxi, ryi, rzi.rstrip()))

        msg.append(pageStamp + str(pageNum) + '\n')
        if f is not None:
            f.write(''.join(msg))
            msg = ['']
        return (''.join(msg), pageNum)

    def _write_f06_transient(self, header, pageStamp, pageNum=1, f=None, isMagPhase=False):
        words = ['                                               C O M P L E X   L O A D   V E C T O R\n',
                 '                                                          (REAL/IMAGINARY)\n',
                 ' \n',
                 '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        #return self.__write_f06_transient_block(words,header,pageStamp,pageNum,f,isMagPhase)
        msg = []
        for dt, translations in sorted(self.translations.iteritems()):
            header[2] = ' %s = %10.4E\n' % (self.data_code['name'], dt)
            msg += header + words
            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                gridType = self.gridTypes[nodeID]

                (dx, dy, dz) = translation
                (rx, ry, rz) = rotation

                if isMagPhase:
                    dxr = abs(dx)
                    dxi = angle(dx, deg=True)
                    dyr = abs(dy)
                    dyi = angle(dy, deg=True)
                    dzr = abs(dz)
                    dzi = angle(dz, deg=True)

                    rxr = abs(rx)
                    rxi = angle(rx, deg=True)
                    ryr = abs(ry)
                    ryi = angle(ry, deg=True)
                    rzr = abs(rz)
                    rzi = angle(rz, deg=True)
                else:
                    dxr = dx.real
                    dyr = dy.real
                    dzr = dz.real
                    dxi = dx.imag
                    dyi = dy.imag
                    dzi = dz.imag

                    rxr = rx.real
                    ryr = ry.real
                    rzr = rz.real
                    rxi = rx.imag
                    ryi = ry.imag
                    rzi = rz.imag

                vals = [dxr, dyr, dzr, rxr, ryr, rzr,
                        dxi, dyi, dzi, rxi, ryi, rzi]
                (vals2, isAllZeros) = writeFloats13E(vals)
                [dxr, dyr, dzr, rxr, ryr, rzr,
                 dxi, dyi, dzi, rxi, ryi, rzi] = vals2
                if not isAllZeros:
                    msg.append('0 %12i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, gridType, dxr, dyr, dzr, rxr, ryr, rzr.rstrip()))
                    msg.append('  %12s %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % ('', '', dxi, dyi, dzi, rxi, ryi, rzi.rstrip()))

            msg.append(pageStamp + str(pageNum) + '\n')
            if f is not None:
                f.write(''.join(msg))
                msg = ['']
            pageNum += 1
        return (''.join(msg), pageNum - 1)

    def __repr__(self):
        return self.write_f06(['', '', ''], 'PAGE ', 1)[0]

        msg = '---COMPLEX LOAD VECTOR---\n'
        #if self.dt is not None:
        #    msg += '%s = %g\n' %(self.data_code['name'],self.dt)
        headers = ['DxReal', 'DxImag', 'DyReal', 'DyImag', 'DzReal', 'DyImag', 'RxReal', 'RxImag', 'RyReal', 'RyImag', 'RzReal', 'RzImag']
        msg += '%-10s ' % ('nodeID')
        for header in headers:
            msg += '%10s ' % (header)
        msg += '\n'

        for freq, translations in sorted(self.translations.iteritems()):
            msg += '%s = %g\n' % (self.data_code['name'], dt)

            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[freq][nodeID]

                msg += '%-10i ' % (nodeID)
                vals = translation + rotation
                for val in vals:
                    if abs(val) < 1e-6:
                        msg += '%10s ' % (0)
                    else:
                        msg += '%10.3e ' % (val)
                msg += '\n'
        return msg


class ThermalVector(TableObject):
    def __init__(self, data_code, is_sort1, isubcase, dt=None):
        TableObject.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_f06(self, header, pageStamp, pageNum=1, f=None, isMagPhase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, pageNum, f)

        msg = header + ['                                              T E M P E R A T U R E   V E C T O R\n',
                        ' \n',
                        '      POINT ID.   TYPE      ID   VALUE     ID+1 VALUE     ID+2 VALUE     ID+3 VALUE     ID+4 VALUE     ID+5 VALUE\n']
        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            gridType = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            (rx, ry, rz) = rotation
            vals = [dx, dy, dz, rx, ry, rz]
            (vals2, isAllZeros) = writeFloats13E(vals)
            if not isAllZeros:
                [dx, dy, dz, rx, ry, rz] = vals2
                msg.append('%14i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, gridType, dx, dy, dz, rx, ry, rz.rstrip()))

        msg.append(pageStamp + str(pageNum) + '\n')
        if f is not None:
            f.write(''.join(msg))
            msg = ['']
        return (''.join(msg), pageNum)

    def _write_f06_transient(self, header, pageStamp, pageNum=1, f=None, isMagPhase=False):
        msg = []
        words = ['                                              T E M P E R A T U R E   V E C T O R\n',
                 ' \n',
                 '      POINT ID.   TYPE      ID   VALUE     ID+1 VALUE     ID+2 VALUE     ID+3 VALUE     ID+4 VALUE     ID+5 VALUE\n']

        for dt, translations in sorted(self.translations.iteritems()):
            header[1] = ' %s = %10.4E\n' % (self.data_code['name'], dt)
            msg += header + words
            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                gridType = self.gridTypes[nodeID]

                (dx, dy, dz) = translation
                (rx, ry, rz) = rotation

                vals = [dx, dy, dz, rx, ry, rz]
                (vals2, isAllZeros) = writeFloats13E(vals)
                if not isAllZeros:
                    [dx, dy, dz, rx, ry, rz] = vals2
                    msg.append('%14i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, gridType, dx, dy, dz, rx, ry, rz.rstrip()))

            msg.append(pageStamp + str(pageNum) + '\n')
            if f is not None:
                f.write(''.join(msg))
                msg = ['']
            pageNum += 1
        return (''.join(msg), pageNum - 1)

    def __reprTransient__(self):
        msg = '---TRANSIENT LOAD VECTOR---\n'
        #msg += '%s = %g\n' %(self.data_code['name'],self.dt)
        msg += self.writeHeader()

        for dt, translations in sorted(self.translations.iteritems()):
            msg += '%s = %g\n' % (self.data_code['name'], dt)
            for nodeID, translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                gridType = self.gridTypes[nodeID]
                (dx, dy, dz) = translation
                (rx, ry, rz) = rotation

                msg += '%-10i %8s ' % (nodeID, gridType)
                vals = [dx, dy, dz, rx, ry, rz]
                for val in vals:
                    if abs(val) < 1e-6:
                        msg += '%10s ' % (0)
                    else:
                        msg += '%10.3e ' % (val)
                msg += '\n'
        return msg

    def __repr__(self):
        if self.nonlinear_factor is not None:
            return self.__reprTransient__()

        msg = '---LOAD VECTOR---\n'
        msg += self.writeHeader()

        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            gridType = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            (rx, ry, rz) = rotation

            msg += '%-10i %-8s ' % (nodeID, gridType)
            vals = [dx, dy, dz, rx, ry, rz]
            for val in vals:
                if abs(val) < 1e-6:
                    msg += '%10s ' % (0)
                else:
                    msg += '%10.3e ' % (val)
            msg += '\n'
        return msg

    def __reprTransient__(self):
        return self._write_f06_transient(['', ''], 'PAGE ', 1)[0]


class ThermalLoadVectorObject(ThermalVector):     # table_code=2, thermal=1
    def __init__(self, data_code, is_sort1, isubcase, dt=None):
        ThermalVector.__init__(self, data_code, is_sort1, isubcase, dt)


class ThermalVelocityVectorObject(ThermalVector):  # table_code=10, thermal=1
    def __init__(self, data_code, is_sort1, isubcase, dt=None):
        ThermalVector.__init__(self, data_code, is_sort1, isubcase, dt)
