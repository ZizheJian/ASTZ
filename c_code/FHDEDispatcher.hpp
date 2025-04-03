#ifndef FHDE_IMPL_SZDISPATCHER_HPP
#define FHDE_IMPL_SZDISPATCHER_HPP

// #include "SZ3/api/impl/SZAlgoInterp.hpp"
// // #include "SZ3/api/impl/SZAlgoLorenzoReg.hpp"
// #include "SZ3/api/impl/SZAlgoNopred.hpp"
// #include "SZ3/utils/Config.hpp"
#include "Statistic.hpp"
#include "FHDEAlgo.hpp"

namespace FHDE {
template <class T, uint N>
size_t FHDE_compress_dispatcher(Config &conf, const T *data, uchar *cmpData, size_t cmpCap) {
    assert(N == conf.N);
    calAbsErrorBound(conf, data);
    size_t cmpSize = 0;
    
    // if absErrorBound is 0, use lossless only mode
    // if (conf.absErrorBound == 0 ) {
    //     conf.cmprAlgo = ALGO_LOSSLESS;
    // }

    // do lossy compression
    bool isCmpCapSufficient = true;
    // if (conf.cmprAlgo != ALGO_LOSSLESS) {
        try {
            std::vector<T> dataCopy(data, data + conf.num);
            if (conf.cmprAlgo == ALGO_FHDE) {
                cmpSize = FHDE_compress_Algo<T, N>(conf, dataCopy.data(), cmpData, cmpCap);
            } else {
                fprintf(stderr, "Unknown compression algorithm\n");
                throw std::invalid_argument("Unknown compression algorithm");
            }

        } catch (std::length_error &e) {
            // if (std::string(e.what()) == SZ_ERROR_COMP_BUFFER_NOT_LARGE_ENOUGH) {
            //     isCmpCapSufficient = false;
            //     printf("SZ is downgraded to lossless mode.\n");
            // } else {
                throw;
            // }
        }
    // }

    return cmpSize;
}


template <class T, uint N>
void FHDE_decompress_dispatcher(Config &conf, const uchar *cmpData, size_t cmpSize, T *decData) {
    // if (conf.cmprAlgo == ALGO_LOSSLESS) {
    //     auto zstd = Lossless_zstd();
    //     size_t decDataSize = 0;
    //     auto decDataPos = reinterpret_cast<uchar *>(decData);
    //     zstd.decompress(cmpData, cmpSize, decDataPos, decDataSize);
    //     if (decDataSize != conf.num * sizeof(T)) {
    //         fprintf(stderr, "Decompressed data size does not match the original data size\n");
    //         throw std::runtime_error("Decompressed data size does not match the original data size");
    //     }
    // } else 
    if (conf.cmprAlgo == ALGO_FHDE) {
        FHDE_decompress_Algo<T, N>(conf, cmpData, cmpSize, decData);
    } else {
        fprintf(stderr, "Unknown compression algorithm\n");
        throw std::invalid_argument("Unknown compression algorithm");
    }
}
}  // namespace FHDE
#endif
