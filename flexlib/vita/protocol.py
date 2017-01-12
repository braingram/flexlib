#!/usr/bin/env python

import struct

from . import const

uint16 = lambda d: struct.unpack('>H', d)[0]
int16 = lambda d: struct.unpack('>h', d)[0]
uint32 = lambda d: struct.unpack('>I', d)[0]
int32 = lambda d: struct.unpack('>i', d)[0]
uint64 = lambda d: struct.unpack('>Q', d)[0]
int64 = lambda d: struct.unpack('>q', d)[0]

float32 = lambda d: struct.unpack('<f', d)[0]


class VitaPacketError(Exception):
    pass


class VitaPacketHeader(object):
    def __init__(self, data):
        self.data = data
        h = uint32(data[:4])
        # TODO do this with struct if it's faster '>BBH'
        self.packet_type = (h >> 28)  # packet type
        self.c = ((h & 0x08000000) != 0)  # class ID present
        self.t = ((h & 0x04000000) != 0)  # trailer present
        self.has_tsi = (h >> 22) & 0x03  # timestamp integer
        self.has_tsf = (h >> 20) & 0x03  # timestamp fractional
        self.count = (h >> 16) & 0xF  # rolling 4-bit counter
        self.packet_size = h & 0xFFFF  # packet size
        self.header_data = h

        self._index = 4
        if (self.packet_type in (
                const.PT_IF_STREAM, const.PT_EXT_STREAM)):
            self.stream_id = uint32(self._next(4))
        else:
            self.stream_id = None
        if self.c:
            self.class_id = VitaClassID(self._next(8))
        else:
            self.class_id = VitaClassID()
        if self.has_tsi != const.TSI_NONE:
            self.tsi = uint32(self._next(4))
        else:
            self.tsi = None
        if self.has_tsf != const.TSF_NONE:
            self.tsf = uint64(self._next(8))
        else:
            self.tsf = None
        self.length = self._index

    def _next(self, n):
        s = self.data[self._index:self._index+n]
        self._index += n
        return s

    def to_json(self):
        d = {}
        for k in self.__dict__:
            if k in ('_index', ):
                continue
            elif k == 'class_id':
                d[k] = self.__dict__[k].to_json()
            elif k not in ('head_data', 'data'):
                d[k] = self.__dict__[k]
        return d


class VitaPacketTrailer(object):
    def __init__(self, data):
        t = uint32(data[-4:])
        # TODO perhaps only parse these when needed as properties
        # TODO if faster, unpack low bits of t, shift and repeat
        self.calibrated_time_enable = (t & 0x80000000) != 0
        self.valid_data_enable = (t & 0x40000000) != 0
        self.reference_lock_enable = (t & 0x20000000) != 0
        self.agcmgc_enable = (t & 0x10000000) != 0
        self.detected_signal_enable = (t & 0x08000000) != 0
        self.spectral_inversion_enable = (t & 0x04000000) != 0
        self.overrange_enable = (t & 0x02000000) != 0
        self.sample_loss_enable = (t & 0x01000000) != 0

        self.calibrated_time_indicator = (t & 0x00080000) != 0
        self.valid_data_indicator = (t & 0x00040000) != 0
        self.reference_lock_indicator = (t & 0x00020000) != 0
        self.agcmgc_indicator = (t & 0x00010000) != 0
        self.detected_signal_indicator = (t & 0x00008000) != 0
        self.spectral_inversion_indicator = (t & 0x00004000) != 0
        self.overrange_indicator = (t & 0x00002000) != 0
        self.sample_loss_indicator = (t & 0x00001000) != 0

        self.e = (t & 0x80) != 0
        self.associated_content_packet_count = t & 0xEF

        self.data = t

    def to_json(self):
        d = {}
        for k in self.__dict__:
            if k != 'data':
                d[k] = self.__dict__[k]
        return d


class VitaClassID(object):
    def __init__(self, data=None):
        if data is None:
            self.oui = None
            self.information_class_code = None
            self.packet_class_code = None
            self.data = None
        else:
            #self.oui, self.information_class_code, self.packet_class_code = \
            #    struct.unpack('>IHH', data[:8])
            #self.oui &= 0x00FFFFFF
            self.oui = uint32(data[:4]) & 0x00FFFFFF
            self.information_class_code = uint16(data[4:6])
            self.packet_class_code = uint16(data[6:8])
            self.data = data

    def to_json(self):
        d = {}
        for k in self.__dict__:
            if k != 'data':
                d[k] = self.__dict__[k]
        return d


class VitaPacket(object):
    def __init__(self, data, header=None):
        self.data = data
        if header is None:
            self.header = VitaPacketHeader(data)
        else:
            self.header = header
        self._index = self.header.length
        """
        if (self.header.packet_type in (
                const.PT_IF_STREAM, const.PT_EXT_STREAM)):
            self.stream_id = uint32(self._next(4))
        else:
            self.stream_id = None
        if self.header.c:
            self.class_id = VitaClassID(self._next(8))
        else:
            self.class_id = VitaClassID()
        if self.header.tsi != const.TSI_NONE:
            self.tsi = uint32(self._next(4))
        else:
            self.tsi = None
        if self.header.tsf != const.TSF_NONE:
            self.tsf = uint64(self._next(8))
        else:
            self.tsf = None
        # remaining data is payload and trailer
        """
        # only parse FLEX packets
        if self.header.class_id.oui == const.FLEX_OUI:
            self._parse_payload()
        if self.header.t:
            self.trailer = VitaPacketTrailer(data)
        else:
            self.trailer = None

    def _next(self, n):
        s = self.data[self._index:self._index+n]
        self._index += n
        return s

    def _parse_payload(self):
        raise NotImplementedError("abstract base class")

    def to_json(self):
        d = {'header': self.header.to_json()}
        if self.trailer is None:
            d['trailer'] = None
        else:
            d['trailer'] = self.trailer.to_json()
        return d


class DiscoveryPacket(VitaPacket):
    def _parse_payload(self):
        #payload_bytes = self.header.packet_size - self._index
        payload_bytes = (self.header.packet_size * 4) - self._index
        if self.header.t:
            payload_bytes -= 4
        # decode UTF8
        self.payload = self.data[
            self._index: self._index + payload_bytes].decode('utf-8')
        self._index += payload_bytes

    def to_json(self):
        d = VitaPacket.to_json(self)
        d['payload'] = self.payload
        return d


class FFTPacket(VitaPacket):
    def _parse_payload(self):
        self.start_bin_index = uint32(self._next(4))
        self.num_bins = uint32(self._next(4))
        self.bin_size = uint32(self._next(4))
        assert self.bin_size == 2
        self.frame_index = uint32(self._next(4))
        # TODO this assumes all bins are 2 bytes, Vita/VitaFFTPacket.cs
        # TODO use numpy.fromstring if endianness matches
        self.payload = [uint16(self._next(2)) for _ in xrange(self.num_bins)]
        self.bins = self.payload

    def to_json(self):
        d = VitaPacket.to_json(self)
        d.update({
            'start_bin_index': self.start_bin_index,
            'num_bins': self.num_bins,
            'bin_size': self.bin_size,
            'frame_index': self.frame_index,
            'bins': self.bins,
        })
        return d


class MeterPacket(VitaPacket):
    def _parse_payload(self):
        #payload_bytes = self.header.packet_size - self._index
        payload_bytes = (self.header.packet_size * 4) - self._index
        if self.header.t:
            payload_bytes -= 4
        if payload_bytes % 4 != 0:
            raise VitaPacketError(
                "Invalid packet size, payload_bytes[%s] not a multiple of 4"
                % (payload_bytes, ))
        self.n = payload_bytes / 4
        self.meters = []
        for _ in xrange(self.n):
            self.meters.append((
                uint16(self._next(2)),
                int16(self._next(2))))

    def to_json(self):
        d = VitaPacket.to_json(self)
        d['meters'] = self.meters
        return d


class WaterfallPacket(VitaPacket):
    def _parse_payload(self):
        self.first_pixel_frequency = int64(self._next(8))
        self.bin_bandwidth = int64(self._next(8))
        self.line_duration_ms = uint32(self._next(4))
        self.width = uint16(self._next(2))
        self.height = uint16(self._next(2))
        self.timecode = uint32(self._next(4))
        self.auto_black_level = uint32(self._next(4))
        #payload_bytes = self.header.packet_size - self._index
        payload_bytes = (self.header.packet_size * 4) - self._index
        if self.header.t:
            payload_bytes -= 4
        self.n = self.width * self.height
        if self.n * 2 != payload_bytes:
            raise VitaPacketError(
                "Invalid packet size, payload_bytes[%s] does not equal "
                "waterfall height * width * 2 [%s]" % (
                    payload_bytes, self.n * 2))
        self.payload = [uint16(self._next(2)) for _ in xrange(self.n)]

    def to_json(self):
        d = VitaPacket.to_json(self)
        d.update({
            'first_pixel_frequency': self.first_pixel_frequency,
            'bin_bandwidth': self.bin_bandwidth,
            'line_duration_ms': self.line_duration_ms,
            'width': self.width,
            'height': self.height,
            'timecode': self.timecode,
            'auto_black_level': self.auto_black_level,
            'payload': self.payload,
        })
        return d


class OpusPacket(VitaPacket):
    def _parse_payload(self):
        #payload_bytes = self.header.packet_size - self._index
        payload_bytes = (self.header.packet_size * 4) - self._index
        # Vita/VitaOpusPacket.cs:118 not sure why 28
        if self.header.t:
            payload_bytes -= 4
        self.payload = self._next(payload_bytes)

    def to_json(self):
        d = VitaPacket.to_json(self)
        d['payload'] = self.payload
        return d


class IFPacket(VitaPacket):
    # private double ONE_OVER_ZERO_DBFS = 1.0 / Math.Pow(2, 15);
    ONE_OVER_ZERO_DBFS = 1.0 / (2 ** 15.)

    def _parse_payload(self):
        #payload_bytes = self.header.packet_size - self._index
        payload_bytes = (self.header.packet_size * 4) - self._index
        if self.header.t:
            payload_bytes -= 4
        self.n = payload_bytes / 4
        if payload_bytes % 4 != 0:
            raise VitaPacketError(
                "Invalid packet size, payload_bytes[%s] not a multiple of 4"
                % (payload_bytes, ))
        # if IF_NARROW, swap bytes
        if (self.header.class_id.packet_class_code & 0x200) == 0:
            self.payload = [
                int32(self._next(4)) * self.ONE_OVER_ZERO_DBFS
                for _ in xrange(self.n)]
        else:
            self.payload = [
                float32(self._next(4)) * self.ONE_OVER_ZERO_DBFS
                for _ in xrange(self.n)]

    def to_json(self):
        d = VitaPacket.to_json(self)
        d['payload'] = self.payload
        return d


packet_types = {
    # radio discovery
    const.VF_DISCOVERY: DiscoveryPacket,
    # signal specs
    const.VF_METER: MeterPacket,
    const.VF_FFT: FFTPacket,
    const.VF_WATERFALL: WaterfallPacket,
    const.VF_OPUS: OpusPacket,
    const.VF_IF_NARROW: IFPacket,
    const.VF_WIDE_24: IFPacket,
    const.VF_WIDE_48: IFPacket,
    const.VF_WIDE_96: IFPacket,
    const.VF_WIDE_192: IFPacket,
}


def parse_packet(data):
    header = VitaPacketHeader(data)
    pclass = packet_types.get(header.class_id.packet_class_code, None)
    if pclass is None:
        raise VitaPacketError(
            "VitaPacket found with unknown type: %s" % (header.packet_type, ))
    return pclass(data, header)
