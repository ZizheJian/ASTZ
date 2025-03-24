#ifndef FHDE_IMPL_SZDISPATCHER_HPP
#define FHDE_IMPL_SZDISPATCHER_HPP

// #include "SZ3/api/impl/SZAlgoInterp.hpp"
// // #include "SZ3/api/impl/SZAlgoLorenzoReg.hpp"
// #include "SZ3/api/impl/SZAlgoNopred.hpp"
// #include "SZ3/utils/Config.hpp"
#include "Statistic.hpp"
#include "FHDEAlgo.hpp"

namespace FHDE{
template <class T,uint N>
size_t FHDE_compress_dispatcher(Config &conf,const T *data,uchar *cmp_data,size_t cmp_cap)
{
    printf("In FHDE_compress_dispatcher\n");
    assert(N==conf.N);
    calAbsErrorBound(conf,data);
    std::vector<T> dataCopy(data,data+conf.num);
    size_t cmp_size=FHDE_compress<T,N>(conf,dataCopy.data(),cmp_data,cmp_cap);
    return cmp_size;
}


// template <class T,uint N>
// void SZ_decompress_dispatcher(Config &conf,const uchar *cmpData,size_t cmp_size,T *decData) {
//     if (conf.cmprAlgo == ALGO_LOSSLESS) {
//         auto zstd=Lossless_zstd();
//         size_t decDataSize=0;
//         auto decDataPos=reinterpret_cast<uchar *>(decData);
//         zstd.decompress(cmpData,cmp_size,decDataPos,decDataSize);
//         if (decDataSize != conf.num * sizeof(T)) {
//             fprintf(stderr,"Decompressed data size does not match the original data size\n");
//             throw std::runtime_error("Decompressed data size does not match the original data size");
//         }
//     } else if (conf.cmprAlgo == ALGO_INTERP) {
//         SZ_decompress_FHDE<T,N>(conf,cmpData,cmp_size,decData);
//     } else if (conf.cmprAlgo == ALGO_NOPRED) {
//         SZ_decompress_nopred<T,N>(conf,cmpData,cmp_size,decData);
//     } else {
//         fprintf(stderr,"Unknown compression algorithm\n");
//         throw std::invalid_argument("Unknown compression algorithm");
//     }
// }
}
#endif
