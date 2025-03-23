#ifndef FHDE_IMPL_SZ_HPP
#define FHDE_IMPL_SZ_HPP

#include "Config.hpp"
#include "zstd/zstd.h"

// #include "SZ3/api/impl/SZDispatcher.hpp"
// #include "SZ3/api/impl/SZImplOMP.hpp"
// #include "SZ3/def.hpp"

namespace FHDE{
// template <class T, uint N>
// size_t SZ_compress_impl(Config &conf, const T *data, uchar *cmpData, size_t cmpCap) {
// #ifndef _OPENMP
//     conf.openmp = false;
// #endif
//     if (conf.openmp) {
//         return SZ_compress_OMP<T, N>(conf, data, cmpData, cmpCap);
//     } else {
//         return SZ_compress_dispatcher<T, N>(conf, data, cmpData, cmpCap);
//     }
// }

// template <class T, uint N>
// void SZ_decompress_impl(Config &conf, const uchar *cmpData, size_t cmpSize, T *decData) {
// #ifndef _OPENMP
//     conf.openmp = false;
// #endif
//     if (conf.openmp) {
//         SZ_decompress_OMP<T, N>(conf, cmpData, cmpSize, decData);
//     } else {
//         SZ_decompress_dispatcher<T, N>(conf, cmpData, cmpSize, decData);
//     }
// }


template<class T>
size_t FHDE_compress_size_bound(const Config &conf)
{
    return conf.size_est() + ZSTD_compressBound(conf.num * sizeof(T));
}

}
#endif
