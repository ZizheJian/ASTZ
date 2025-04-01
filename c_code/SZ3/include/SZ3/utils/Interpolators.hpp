//
// Created by Kai Zhao on 9/1/20.
//

#ifndef SZ_INTERPOLATORS_HPP
#define SZ_INTERPOLATORS_HPP

#include "SZ3/def.hpp"
// #include "SZ3/decomposition/FHDEDecomposition.hpp"
#include "SZ3/quantizer/Quantizer.hpp"
#include "SZ3/utils/Config.hpp"
#include "SZ3/utils/FileUtil.hpp"
#include "SZ3/utils/Iterator.hpp"
#include "SZ3/utils/MemoryUtil.hpp"
#include "SZ3/utils/Timer.hpp"
#include <stdlib.h>

namespace SZ3 {
template <class T>
inline T interp_linear(T a, T b, float c1, float c2) {
    return (a * c1 + b * c2);
}

template <class T>
inline T interp_linear1(T a, T b) {
    return -0.5 * a + 1.5 * b;
}

template <class T>
inline T interp_linear_2d(T a, T a_left, T a_right, T b, T b_left, T b_right) {
    // return (a + a_left + a_right + b + b_left + b_right) / 6;
    return (a + b) / 6;
}

template <class T>
inline T interp_linear_2d_22x(T a_botleft, T a_botright, T a_topleft, T a_topright) {
    // return (a + a_left + a_right + b + b_left + b_right) / 6;
    return (a_botleft + a_botright + a_topleft + a_topright) / 4;
}

template <class T>
inline T interp_linear_2d_24x(T a_botleft, T a_botright, T a_topleft, T a_topright, T b_botleft, T b_botright, T b_topleft, T b_topright) {
    // return (a + a_left + a_right + b + b_left + b_right) / 6;
    return (a_botleft + a_botright + a_topleft + a_topright + b_botleft + b_botright + b_topleft + b_topright) / 8;
}

template <class T>
inline T interp_linear_2d_22x_corner1(T a_botleft, T a_botright) {
    // return (a + a_left + a_right + b + b_left + b_right) / 6;
    return (a_botleft + a_botright) / 2;
}

template <class T>
inline T interp_linear_2d_22x_corner2(T a_botleft) {
    // return (a + a_left + a_right + b + b_left + b_right) / 6;
    return a_botleft;
}


template <class T>
inline T interp_linear1_2d(T a, T a_left, T a_right) {
    // return (a + a_left + a_right) / 3;
    return a;
}

template <class T>
inline T interp_linear_3d(T a, T a_1, T a_2, T a_3, T a_4, T a_5, T a_6, T a_7, T a_8, T b, T b_1, T b_2, T b_3, T b_4, T b_5, T b_6, T b_7, T b_8) {
    return (a + a_1 + a_2 + a_3 + a_4 + a_5 + a_6 + a_7 + a_8 + b + b_1 + b_2 + b_3 + b_4 + b_5 + b_6 + b_7 + b_8) / 18;
}

template <class T>
inline T interp_linear1_3d(T a, T a_1, T a_2, T a_3, T a_4, T a_5, T a_6, T a_7, T a_8) {
    return (a + a_1 + a_2 + a_3 + a_4 + a_5 + a_6 + a_7 + a_8) / 9;
}

template <class T>
inline T interp_quad_1(T a, T b, T c) {
    return (3 * a + 6 * b - c) / 8;
}

template <class T>
inline T interp_quad_2(T a, T b, T c) {
    return (-a + 6 * b + 3 * c) / 8;
}

template <class T>
inline T interp_quad_3(T a, T b, T c) {
    return (3 * a - 10 * b + 15 * c) / 8;
}

template <class T>
inline T interp_cubic(T a, T b, T c, T d) {
    return (-a + 9 * b + 9 * c - d) / 16;
}

template <class T>
inline T interp_cubic_front(T a, T b, T c, T d) {
    return (5 * a + 15 * b - 5 * c + d) / 16;
}

template <class T>
inline T interp_cubic_front_2(T a, T b, T c, T d) {
    return (a + 6 * b - 4 * c + d) / 4;
}

template <class T>
inline T interp_cubic_back_1(T a, T b, T c, T d) {
    return (a - 5 * b + 15 * c + 5 * d) / 16;
}

template <class T>
inline T interp_cubic_back_2(T a, T b, T c, T d) {
    return (-5 * a + 21 * b - 35 * c + 35 * d) / 16;
}

template <class T>
inline T interp_cubic2(T a, T b, T c, T d) {
    return (-3 * a + 23 * b + 23 * c - 3 * d) / 40;
}

template <class T>
inline T interp_akima(T a, T b, T c, T d) {
    T t0 = 2 * b - a - c;
    T t1 = 2 * c - b - d;
    T abt0 = fabs(t0);
    T abt1 = fabs(t1);
    if (fabs(abt0 + abt1) > 1e-9) {
        return (b + c) / 2 + (t0 * abt1 + t1 * abt0) / 8 / (abt0 + abt1);
    } else {
        return (b + c) / 2;
    }
}

template <class T>
inline T interp_pchip(T a, T b, T c, T d) {
    T pchip = (b + c) / 2;
    if ((b - a < 0) == (c - b < 0) && fabs(c - a) > 1e-9) {
        pchip += 1 / 4 * (b - a) * (c - b) / (c - a);
    }
    if ((c - b < 0) == (d - c < 0) && fabs(d - b) > 1e-9) {
        pchip -= 1 / 4 * (c - b) * (d - c) / (d - b);
    }
    return pchip;
}

// template <class T>
// inline T inner_prod(std::vector<T> v, std::vector<_Float32> a) {
//     for()
//     return (a * c1 + b * c2);
// }

template <class T>
inline T interp_linear_3(T a1, T a2, T a3, float w1, float w2, float w3) {
    return a1 * w1 + a2 * w2 + a3 * w3;
}

template <class T>
inline T interp_linear_4(T a1, T a2, T a3, T a4, float w1, float w2, float w3, float w4) {
    return a1 * w1 + a2 * w2 + a3 * w3 + a4 * w4;
}

template <class T>
inline T interp_linear_6(T a1, T a2, T a3, T a4, T a5, T a6,
                         float w1, float w2, float w3, float w4, float w5, float w6) {
    return a1 * w1 + a2 * w2 + a3 * w3 + a4 * w4 + a5 * w5 + a6 * w6;
}

template <class T>
inline T interp_linear_12(T a1, T a2, T a3, T a4, T a5, T a6,
                          T a7, T a8, T a9, T a10, T a11, T a12,
                          float w1, float w2, float w3, float w4, float w5, float w6,
                          float w7, float w8, float w9, float w10, float w11, float w12) {
    return a1 * w1 + a2 * w2 + a3 * w3 + a4 * w4 + a5 * w5 + a6 * w6 +
           a7 * w7 + a8 * w8 + a9 * w9 + a10 * w10 + a11 * w11 + a12 * w12;
}

}  // namespace SZ3
#endif  // SZ_INTERPOLATORS_HPP
