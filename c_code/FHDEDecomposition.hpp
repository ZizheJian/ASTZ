#ifndef _SZ_INTERPOLATION_DECOMPOSITION_HPP
#define _SZ_INTERPOLATION_DECOMPOSITION_HPP

#include <cmath>
#include <cstring>

#include "Decomposition.hpp"
#include "def.hpp"
#include "Quantizer.hpp"
#include "Config.hpp"
#include "FileUtil.hpp"
#include "Interpolators.hpp"
#include "Iterator.hpp"
#include "MemoryUtil.hpp"
#include "Timer.hpp"
#include "ParamTuning.hpp"
#include <fstream>
namespace FHDE {

enum PredictorBehavior { PB_predict_overwrite, PB_predict, PB_recover };


template <class T, uint N, class Quantizer>
class FHDEDecomposition : public concepts::DecompositionInterface<T, int, N> {
   public:
    FHDEDecomposition(const Config &conf, Quantizer quantizer) : quantizer(quantizer) {
        static_assert(std::is_base_of<concepts::QuantizerInterface<T, int>, Quantizer>::value,
                      "must implement the quantizer interface");
        if(conf.tpPath != nullptr) {
            tpPath = conf.tpPath;
        } else {
            throw;
        }
    }

    T *decompress(const Config &conf, std::vector<int> &quant_inds, T *dec_data) override {
        
        init();

        this->quant_inds = quant_inds.data();
        //            lossless.postdecompress_data(buffer);
        double eb = quantizer.get_eb();

        *dec_data = quantizer.recover(0, this->quant_inds[quant_index++]);

        interpolation_level = level_dimensions.size();
        std::array<int, 4> last_dim = {1, 1, 1, 1};
        int last_dir = 0;
        state S = state::Z;

        for (uint level = interpolation_level - 1; level >= 0 && level < interpolation_level; level--) {
           
            quantizer.set_eb(eb * pow(0.95, level));
            // } else {
            //     quantizer.set_eb(0);
            // }
            
            // { // Log
            //     std::cout << level << std::endl;
            // }
            // size_t stride = 1U << (level - 1);

            std::array<int, 3> strides = calc_stride(level_dimensions[level]);
            int dir = 0;
            int dir2 = 0;
            bool foundone = false;
            bool foundtwo = false;
            bool found3 = false;
            { // predict behavier
                
                for(int i = 0; i < 3; i++) {
                    if(level_dimensions[level][i] > last_dim[i]){
                        if(foundtwo) {
                            found3 = true;
                        } else if(foundone) {
                            dir2 = i;
                            foundtwo = true;
                        } else {
                            dir = i;
                        }
                        foundone = true;
                    }
                }
                // int last_digit = (level_dimensions[level][3] % 10);
                switch (S)
                {
                case state::Z:
                    if(found3) {
                        // std::cout << "in state A0" << std::endl;
                        
                        S = state::A;
                    } else if(foundtwo) {
                        S = state::B;
                    } else if(foundone) {
                        S = state::C;
                    } else {
                        // std::cout << "waa1" << std::endl;
                    }
                    break;
                case state::C:
                    if(found3) {
                        // std::cout << "waa2" << std::endl;
                    } else if(foundtwo) {
                        S = state::A;
                    } else if(foundone) {
                        S = state::B;
                    } else {
                        // std::cout << "waa3" << std::endl;
                    }
                    break;
                case state::E:
                    if(found3) {
                        // std::cout << "waa4" << std::endl;
                    } else if(foundtwo) {
                        // std::cout << "waa5" << std::endl;
                    } else if(foundone) {
                        S = state::D;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::D:
                    if(found3) {
                        // std::cout << "waa6" << std::endl;
                    } else if(foundtwo) {
                        // std::cout << "waa7" << std::endl;
                    } else if(foundone) {
                        // std::cout << "waa8" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::A:
                    // std::cout << "in state A" << std::endl;

                    if(foundone) {
                        // std::cout << "waa9" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::F:
                    if(foundone) {
                        // std::cout << "waa10" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::G:
                    if(foundone) {
                        // std::cout << "waa11" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                default:
                    break;
                }
                last_dim = level_dimensions[level];
            }
            
            std::vector<std::array<int, 3>> begins, ends;
            // std::cout << level_dimensions[level][0] << ' ' << level_dimensions[level][1] << ' ' << level_dimensions[level][2] << std::endl;
            block_divider(level_dimensions[level], begins, ends);
            // std::cout << begins.size() << ' ' << ends.size() << std::endl;
            if(foundtwo) dir = 3 - dir - dir2;

            for(int i = 0; i < begins.size(); i++) {

                {

                    params = std::vector<double>(coeff_list[coeff_idx].begin(), coeff_list[coeff_idx].end());
                    // std::cout << params.size() << std::endl;
                    int param_size = params.size() - 4;
                    double baseline = 1.0 / param_size;
                    for(int k = 0; k < param_size; k++) {
                        params[k] += baseline;
                    }
                }
                
                if(S == state::A) {
                    // dir = 3 - (level_dimensions[level][3] % 10);
                    dir = (level_dimensions[level][3] % 10) - 1;
                    if(level_dimensions[level][3] > 130 && level_dimensions[level][3] < 140) {
                        interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                        coeff_idx++;
                    } else {
                        interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                    }
                } else if(S == state::B) {
                    // params = std::vector<double>(coeff_list[coeff_idx].begin(), coeff_list[coeff_idx].end());
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 221, strides, dir);
                    // coeff_idx++;
                } else if (S == state::C) {

                    dir = foundone ? dir : last_dir;
                    // params = {0.5, 0.5};
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 411, strides, dir);
                    coeff_idx++;

                } else if(S == state::E) {
                    dir = (level_dimensions[level][3] % 10) - 1;
                    // interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 231, strides, last_dir);
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 231, strides, dir);
                    coeff_idx++;
                } else if(S == state::D) {
                    dir = 3 - (level_dimensions[level][3] % 10);
                    if(level_dimensions[level][3] > 420) {
                        interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 421, strides, dir);
                        coeff_idx++;
                    } else if(level_dimensions[level][3] > 250) {
                        // params = {0.5, 0.5};
                        interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 251, strides, dir);
                        coeff_idx++;

                    } else {    // 24x
                        interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                        coeff_idx++;

                    } 
                } else if(S == state::F) {
                    dir = 3 - (level_dimensions[level][3] % 10);
                    // std::cout << "(decmp) from F: " << "dir = " << dir << std::endl;
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 431, strides, dir);
                    coeff_idx++;

                } else if(S == state::G) {
                    // dir = (level_dimensions[level][3] % 10) - 1;
                    dir = 3 - (level_dimensions[level][3] % 10);
                    // std::cout << "from G: " << "dir = " << dir << std::endl;
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                    coeff_idx++;
                }

                // { // Log
                //     std::cout << "quant_index: " << quant_index << std::endl;
                // }
            }
            last_dir = dir;

            { // state transfer
                switch (S)
                {
                case state::C:
                    S = state::Z;
                    break;
                case state::B:
                    S = state::E;
                    break;
                case state::E:
                    S = state::Z;
                    break;
                case state::D:
                    if(level_dimensions[level][3] > 420) {S = state::C; }
                    else if(level_dimensions[level][3] > 250) {S = state::E;}
                    else {S = state::F;}
                    break;
                case state::A:
                    if(level_dimensions[level][3] > 130) {
                        S = state::G;
                    } else {
                        S = state::D;
                    }
                    break;
                case state::F:
                    S = state::Z;
                    break;
                case state::G:
                    S = state::E;
                    break;
                default:
                    break;
                }
            }
        
        }


        quantizer.postdecompress_data();
        //            timer.stop("Interpolation Decompress");
        std::vector<T> arr(dec_data, dec_data + conf.num);
        denormalize(arr, norm_min, norm_max);
        for(int i = 0; i < conf.num; i++) dec_data[i] = arr[i];
        return dec_data;
    }

    void block_divider(std::array<int, 4> level_size, std::vector<std::array<int, 3>>& begins, std::vector<std::array<int, 3>>& ends) {
        int blocklimit = 32;

        for(int i = 0; i*blocklimit < level_size[0]; i++) {
            int block_begin_x = i*blocklimit;
            int block_end_x = std::min((i + 1)*blocklimit, level_size[0] - 1);
            for(int j = 0; j*blocklimit < level_size[1]; j++) {
                int block_begin_y = j*blocklimit;
                int block_end_y = std::min((j + 1)*blocklimit, level_size[1] - 1);
                for(int k = 0; k*blocklimit < level_size[2]; k++) {
                    int block_begin_z = k*blocklimit;
                    int block_end_z = std::min((k + 1)*blocklimit, level_size[2] - 1);
                    begins.push_back(std::array<int, 3>{block_begin_x, block_begin_y, block_begin_z});
                    ends.push_back(std::array<int, 3>{block_end_x, block_end_y, block_end_z});
                }
            }
        }
    }
    // compress given the error bound
    std::vector<int> compress(const Config &conf, T *data) override {
        std::vector<T> arr(data, data + conf.num);
        normalize(arr, norm_min, norm_max);
        data = arr.data();
        
        bool fixed_param_mode = false; // 
        std::copy_n(conf.dims.begin(), N, global_dimensions.begin());
        blocksize = 32;
        // blocksize = 65536;
        interpolator_id = conf.interpAlgo;
        direction_sequence_id = conf.interpDirection;

        init();


        std::vector<int> quant_inds_vec(num_elements);
        quant_inds = quant_inds_vec.data();

        quantizer.set_eb(quantizer.get_eb() / (norm_max - norm_min) * 2.0);
        double eb = quantizer.get_eb();
        

        //            quant_inds.push_back(quantizer.quantize_and_overwrite(*data, 0));
        quant_inds[quant_index++] = quantizer.quantize_and_overwrite(*data, 0);

        //            Timer timer;
        //            timer.start();
        // int temp = interpolation_level;
        interpolation_level = level_dimensions.size();
        std::array<int, 4> last_dim = {1, 1, 1, 1};
        int last_dir = 0;
        state S = state::Z;

        for (uint level = interpolation_level - 1; level >= 0 && level < interpolation_level; level--) {
            // if (level >= 3) {
            //     quantizer.set_eb(eb * eb_ratio);
            // } else {
            //     quantizer.set_eb(eb);
            // }
            // if(interpolation_level - 1 - level > 9) {
            quantizer.set_eb(eb * pow(0.95, level));
            // } else {
            //     quantizer.set_eb(0);
            // }

            // { // Log
            //     std::cout << level << std::endl;
            // }
            // size_t stride = 1U << (level - 1);
            // std::cout << "hh\n";

            std::array<int, 3> strides = calc_stride(level_dimensions[level]);
            int dir = 0;
            int dir2 = 0;
            bool foundone = false;
            bool foundtwo = false;
            bool found3 = false;
            { // predict behavier
                
                for(int i = 0; i < 3; i++) {
                    if(level_dimensions[level][i] > last_dim[i]){
                        if(foundtwo) {
                            found3 = true;
                        } else if(foundone) {
                            dir2 = i;
                            foundtwo = true;
                        } else {
                            dir = i;
                        }
                        foundone = true;
                    }
                }
                // int last_digit = (level_dimensions[level][3] % 10);
                switch (S)
                {
                case state::Z:
                    if(found3) {
                        // std::cout << "in state A0" << std::endl;
                        
                        S = state::A;
                    } else if(foundtwo) {
                        S = state::B;
                    } else if(foundone) {
                        S = state::C;
                    } else {
                        // std::cout << "waa1" << std::endl;
                    }
                    break;
                case state::C:
                    if(found3) {
                        // std::cout << "waa2" << std::endl;
                    } else if(foundtwo) {
                        S = state::A;
                    } else if(foundone) {
                        S = state::B;
                    } else {
                        // std::cout << "waa3" << std::endl;
                    }
                    break;
                case state::E:
                    if(found3) {
                        // std::cout << "waa4" << std::endl;
                    } else if(foundtwo) {
                        // std::cout << "waa5" << std::endl;
                    } else if(foundone) {
                        S = state::D;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::D:
                    if(found3) {
                        // std::cout << "waa6" << std::endl;
                    } else if(foundtwo) {
                        // std::cout << "waa7" << std::endl;
                    } else if(foundone) {
                        // std::cout << "waa8" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::A:
                    // std::cout << "in state A" << std::endl;

                    if(foundone) {
                        // std::cout << "waa9" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::F:
                    if(foundone) {
                        // std::cout << "waa10" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                    break;
                case state::G:
                    if(foundone) {
                        // std::cout << "waa11" << std::endl;
                    } else {
                        // std::cout << "waa" << std::endl;
                    }
                default:
                    break;
                }
                last_dim = level_dimensions[level];
            }
            
            std::vector<std::array<int, 3>> begins, ends;
            // std::cout << level_dimensions[level][0] << ' ' << level_dimensions[level][1] << ' ' << level_dimensions[level][2] << std::endl;
            block_divider(level_dimensions[level], begins, ends);
            // std::cout << begins.size() << ' ' << ends.size() << std::endl;
            if(foundtwo) dir = 3 - dir - dir2;

            size_t quant_sz_1 = quant_index;

            for(int i = 0; i < begins.size(); i++) {
                // std::cout << "block" << i << ": " << begins[i][0] << ' ' << begins[i][1] << ' ' << begins[i][2] << " to " << ends[i][0] << ' ' << ends[i][1] << ' ' << ends[i][2] << std::endl;
                if(S == state::A) {
                    dir = (level_dimensions[level][3] % 10) - 1;
                    // dir = 3 - (level_dimensions[level][3] % 10);
                    if(level_dimensions[level][3] > 130 && level_dimensions[level][3] < 140) {
                        interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                        {   // train
                            std::vector<double> w = {0.125, 0.125, 0.125, 0.125, 
                                                    0.125, 0.125, 0.125, 0.125, 
                                                    0, 0, 0, 0};
                            if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                                params = w;
                            } else {
                                params = {0.125, 0.125, 0.125, 0.125, 
                                        0.125, 0.125, 0.125, 0.125, 
                                        0, 0, 0, 0};
                            }
                        }
                        { // save params
                            std::vector<_Float32> float_params(params.begin(), params.end());
                            int param_size = float_params.size() - 4;
                            _Float32 baseline = 1.0 / (param_size);
                            for(int k = 0; k < param_size; k++) {
                                float_params[k] -= baseline;
                            }
                            coeff_list.push_back(float_params);
                            coeff_idx++;
                        }
                        interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                    } else {
                        interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                    }
                } else if(S == state::B) {
                    // std::cout << "quant_sz_1: " << quant_sz_1 << std::endl;
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 221, strides, dir);
                    // std::cout << "x_s_size: " << x_s.size() << std::endl;

                    // for(int k = 0; k < x_s.size(); k++) {
                    //     std::cout << "x_s " << k << " " << x_s[k][0] << ' ' << x_s[k][1] << ' ' << x_s[k][2] << ' ' << x_s[k][3] << std::endl; 
                    //     std::cout << "y_s " << k << " " << y_s[k] << std::endl; 
                    // }

                } else if (S == state::C) {
                    dir = foundone ? dir : last_dir;

                    interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], 411, strides, dir);
                    {   // train
                        int k = 2;
                        std::vector<double> w = {0.5, 0.5, 0, 0, 0, 0};
                        if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                            params = w;

                        } else {
                            params = {0.5, 0.5, 0, 0, 0, 0};
                        }
                    }
                    // params = {0.5, 0.5};
                    { // save params
                        std::vector<_Float32> float_params(params.begin(), params.end());
                        int param_size = float_params.size() - 4;
                        _Float32 baseline = 1.0 / (param_size);
                        for(int k = 0; k < param_size; k++) {
                            float_params[k] -= baseline;
                        }
                        coeff_list.push_back(float_params);
                        coeff_idx++;
                    }
                    // coeff_list.push_back(float_params);
                    // coeff_idx++;
                    // std::cout << "coeff actual size = " << coeff_list.size() << std::endl;
                    // std::cout << "param0 = " << params[0] << " p1 = " << params[1] << " cmp coeff=" << coeff_idx << std::endl;
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 411, strides, dir);
                } else if(S == state::E) {
                    dir = (level_dimensions[level][3] % 10) - 1;
                    // std::cout << "_23x " << "dir = " << dir << std::endl;
                    interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], 231, strides, dir);
                    {   // train
                        std::vector<double> w = {0.25, 0.25, 0.25, 0.25, 0, 0, 0, 0};
                        if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                            params = w;
                            // std::cout << "23x param = " << params[0] << ", " << params[1] << "; " << params[2] << " " << params[3] << " " << params[4] << " " << params[5] << " cmp coeff=" << coeff_idx << std::endl;
                        } else {
                            params = {0.25, 0.25, 0.25, 0.25, 0, 0, 0, 0};
                        }
                    }
                    { // save params
                        std::vector<_Float32> float_params(params.begin(), params.end());
                        int param_size = float_params.size() - 4;
                        _Float32 baseline = 1.0 / (param_size);
                        for(int k = 0; k < param_size; k++) {
                            float_params[k] -= baseline;
                        }
                        coeff_list.push_back(float_params);
                        coeff_idx++;
                    }
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 231, strides, dir);
                } else if(S == state::D) {
                    dir = 3 - (level_dimensions[level][3] % 10);
                    // std::cout << "from D: " << "dir = " << dir << std::endl;
                    if(level_dimensions[level][3] > 420) {
                        interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], 421, strides, dir);
                        {   // train
                            std::vector<double> w = {0.25, 0.25, 0.25, 0.25, 0, 0, 0, 0};
                            if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                                params = w;
                                // std::cout << "42x param = " << params[0] << ", " << params[1] << "; " << params[2] << " " << params[3] << " " << params[4] << " " << params[5] << " cmp coeff=" << coeff_idx << std::endl;
                            } else {
                                params = {0.25, 0.25, 0.25, 0.25, 0, 0, 0, 0};
                            }
                        }
                        { // save params
                            std::vector<_Float32> float_params(params.begin(), params.end());
                            int param_size = float_params.size() - 4;
                            _Float32 baseline = 1.0 / (param_size);
                            for(int k = 0; k < param_size; k++) {
                                float_params[k] -= baseline;
                            }
                            coeff_list.push_back(float_params);
                            coeff_idx++;
                        }
                        interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 421, strides, dir);
                    } else if(level_dimensions[level][3] > 250) {
                        // std::cout << "_25x " << "dir = " << dir << std::endl;
                        interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], 251, strides, dir);
                        {   // train
                            std::vector<double> w = {0.5, 0.5, 0, 0, 0, 0};
                            if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                                params = w;
                                // std::cout << "25x param = " << params[0] << ", " << params[1] << "; " << params[2] << " " << params[3] << " " << params[4] << " " << params[5] << " cmp coeff=" << coeff_idx << std::endl;
                            } else {
                                params = {0.5, 0.5, 0, 0, 0, 0};
                            }
                        }
                        { // save params
                            std::vector<_Float32> float_params(params.begin(), params.end());
                            int param_size = float_params.size() - 4;
                            _Float32 baseline = 1.0 / (param_size);
                            for(int k = 0; k < param_size; k++) {
                                float_params[k] -= baseline;
                            }
                            coeff_list.push_back(float_params);
                            coeff_idx++;
                        }
                        interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 251, strides, dir);
                    } else { // 24x
                        interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                        {   // train
                            std::vector<double> w = {0.125, 0.125, 0.125, 0.125, 
                                                    0.125, 0.125, 0.125, 0.125, 
                                                    0, 0, 0, 0};
                            if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                                params = w;
                            } else {
                                params = {0.125, 0.125, 0.125, 0.125, 
                                        0.125, 0.125, 0.125, 0.125, 
                                        0, 0, 0, 0};
                            }
                        }
                        { // save params
                            std::vector<_Float32> float_params(params.begin(), params.end());
                            int param_size = float_params.size() - 4;
                            _Float32 baseline = 1.0 / (param_size);
                            for(int k = 0; k < param_size; k++) {
                                float_params[k] -= baseline;
                            }
                            coeff_list.push_back(float_params);
                            coeff_idx++;
                        }
                        interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                    }
                } else if(S == state::F) {
                    dir = 2;
                    // dir = 3 - (level_dimensions[level][3] % 10);

                    // std::cout << "from F: " << "dir = " << dir << std::endl;
                    interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], 431, strides, dir);
                    {   // train
                        std::vector<double> w = {0.167, 0.167, 0.167, 0.167, 0.167, 0.167, 
                                                0, 0, 0, 0};
                        if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                            params = w;
                        } else {
                            params = {1.0 / 6, 1.0 / 6, 1.0 / 6, 1.0 / 6, 1.0 / 6, 1.0 / 6, 
                                    0, 0, 0, 0};
                        }
                    }
                    { // save params
                        std::vector<_Float32> float_params(params.begin(), params.end());
                        int param_size = float_params.size() - 4;
                        _Float32 baseline = 1.0 / (param_size);
                        for(int k = 0; k < param_size; k++) {
                            float_params[k] -= baseline;
                        }
                        coeff_list.push_back(float_params);
                        coeff_idx++;
                    }
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 431, strides, dir);
                } else if(S == state::G) {
                    dir = 3 - (level_dimensions[level][3] % 10);
                    // std::cout << "from G: " << "dir = " << dir << std::endl;
                    // std::cout << "_25x " << "dir = " << dir << std::endl;
                    interpolation(data, begins[i], ends[i], PB_predict, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                    {   // train
                        std::vector<double> w = {0.5, 0.5, 0, 0, 0, 0};
                        if(!fixed_param_mode && x_s.size() && !robustRidgeRegression(x_s, y_s, w, lambda, filter_threshold * eb * pow(0.95, level))) {
                            params = w;
                            // std::cout << "26x param = " << params[0] << ", " << params[1] << "; " << params[2] << " " << params[3] << " " << params[4] << " " << params[5] << " cmp coeff=" << coeff_idx << std::endl;
                        } else {
                            params = {0.5, 0.5, 0, 0, 0, 0};
                        }
                    }
                    { // save params
                        std::vector<_Float32> float_params(params.begin(), params.end());
                        int param_size = float_params.size() - 4;
                        _Float32 baseline = 1.0 / (param_size);
                        for(int k = 0; k < param_size; k++) {
                            float_params[k] -= baseline;
                        }
                        coeff_list.push_back(float_params);
                        coeff_idx++;
                    }
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], level_dimensions[level][3], strides, dir);
                }
                // { // Log
                //     std::cout << "quant_index: " << quant_index << std::endl;
                // }
            }
            last_dir = dir;

            { // state transfer
                switch (S)
                {
                case state::C:
                    S = state::Z;
                    break;
                case state::B:
                    S = state::E;
                    break;
                case state::E:
                    S = state::Z;
                    break;
                case state::D:
                    if(level_dimensions[level][3] > 420) {S = state::C; }
                    else if(level_dimensions[level][3] > 250) {S = state::E;}
                    else {S = state::F;}
                    break;
                case state::A:
                    if(level_dimensions[level][3] > 130) {
                        S = state::G;
                    } else {
                        S = state::D;
                    }
                    break;
                case state::F:
                    S = state::Z;
                    break;
                case state::G:
                    S = state::E;
                    break;
                default:
                    break;
                }
            }
        }


        quantizer.postcompress_data();
        return quant_inds_vec;
    }

    void save(uchar *&c) override {
        write(global_dimensions.data(), N, c);
        write(blocksize, c);
        write(interpolator_id, c);
        write(direction_sequence_id, c);

        write(norm_min, c);
        write(norm_max, c);
        write(coeff_list.size(), c);
        for(int i = 0; i < coeff_list.size(); i++) {
            write(coeff_list[i].size(), c);
            write(coeff_list[i].data(), coeff_list[i].size(), c);
        }
        quantizer.save(c);
    }

    void load(const uchar *&c, size_t &remaining_length) override {
        read(global_dimensions.data(), N, c, remaining_length);
        read(blocksize, c, remaining_length);
        read(interpolator_id, c, remaining_length);
        read(direction_sequence_id, c, remaining_length);

        read(norm_min, c);
        read(norm_max, c);
        size_t coeff_size = 0;
        read(coeff_size, c, remaining_length);
        coeff_list.resize(coeff_size);
        std::cout << "coeffsize = " << coeff_size << std::endl;

        for(int i = 0; i < coeff_size; i++) {
            size_t J = 0;
            read(J, c, remaining_length);
            coeff_list[i].resize(J);
            read(coeff_list[i].data(), J, c, remaining_length);
        }
        quantizer.load(c, remaining_length);
    }

    std::pair<int, int> get_out_range() override { return quantizer.get_out_range(); }

   private:
    

    std::array<int, 3> calc_stride(std::array<int, 4>& dim) {
        std::array<int, 3> strides;
        for(int i = 0; i < 3; i++) {
            if(dim[i] == 1){
                strides[i] = 0;
                continue;
            }
            for(int shift = 0; shift < 30; shift++) {
                int stride = 1 << shift;
                bool cond1 = (dim[i] - 1) * stride <= global_dimensions[i] - 1;
                bool cond2 = dim[i] * stride > global_dimensions[i] - 1;
                if(cond1 && cond2) {
                    strides[i] = stride;
                    break;
                }
            }
        }
        return strides;
    }

    void level_dimension_loader() {
        std::ifstream infile(tpPath); 
        std::string line;

        while (std::getline(infile, line)) {
            std::istringstream iss(line);
            std::array<int, 4> values;
            if (iss >> values[0] >> values[1] >> values[2] >> values[3]) {
                level_dimensions.push_back(values);
            } else {
                std::cerr << "格式错误: " << line << std::endl;
            }
        }

        // for (auto arr : level_dimensions) {
            // for (int val : arr) {
            //     std::cout << val << " ";
            // }
            // std::cout << '\n';
            // std::array<int, 3> strides = calc_stride(arr);
            // std::cout << "stride: ";
            // for (int val : strides) {
            //     std::cout << val << " ";
            // }
            // std::cout <<"\n\n";
        // }
    }
    
    void init() {
        quant_index = 0;
        assert(blocksize % 2 == 0 && "Interpolation block size should be even numbers");
        num_elements = 1;
        interpolation_level = -1;
        for (int i = 0; i < N; i++) {
            if (interpolation_level < ceil(log2(global_dimensions[i]))) {
                interpolation_level = static_cast<uint>(ceil(log2(global_dimensions[i])));
            }
            num_elements *= global_dimensions[i];
        }

        dimension_offsets[N - 1] = 1;
        for (int i = N - 2; i >= 0; i--) {
            dimension_offsets[i] = dimension_offsets[i + 1] * global_dimensions[i + 1];
        }

        dimension_sequences = std::vector<std::array<int, N>>();
        auto sequence = std::array<int, N>();
        for (int i = 0; i < N; i++) {
            sequence[i] = i;
        }
        do {
            dimension_sequences.push_back(sequence);
        } while (std::next_permutation(sequence.begin(), sequence.end()));
        // std::cout << global_dimensions[0] << ' ' << global_dimensions[1] << ' ' << global_dimensions[2] << std::endl;
        level_dimension_loader();
    }

    inline void quantize(size_t idx, T &d, T pred) {
        // {   // debug
        //     if(quant_index < 100) {
        //         std::cout << "(x, y, z) = (" << idx/(96*96) << ", " << (idx % (96*96))/96 << ", " << (idx % 96) << ")" << std::endl;
        //     }
        // }
        
        quant_inds[quant_index++] = (quantizer.quantize_and_overwrite(d, pred));
    }

    inline void recover(size_t idx, T &d, T pred) { d = quantizer.recover(pred, quant_inds[quant_index++]); }
    
    double block_interpolation_1d_mid(T *data, size_t begin, size_t end, size_t stride, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        
        size_t n = (end - begin) / stride + 1;
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << " n=" << n<< std::endl;
        // }
        if (n <= 1) {
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            // std::cout << "a1" << std::endl;

            for (size_t i = 1; i < n; i += 2) {
                // std::cout << "a2" << std::endl;

                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                // quantize(d - data, *d, interp_linear_3(*(d - stride) * 1.0, *(d + stride) * 1.0, 1.0, params[0], params[1], params[2]));
                // quantize(d - data, *d, interp_linear_4(*(d - stride) * 1.0, *(d + stride) * 1.0, i / 32.0, log2(stride), params[0], params[1], params[2], params[3]));
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                quantize(d - data, *d, interp_linear_6(*(d - stride) * 1.0, *(d + stride) * 1.0, x*1.0, y*1.0, z*1.0, 1.0, params[0], params[1], params[2], params[3], params[4], params[5]));

            }
                // std::cout << "a3" << std::endl;

            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;

                if (n < 4) {
                    // std::cout << "n=2\n" << std::endl;
                    quantize(d - data, *d, *(d - stride));
                } 
            }
        } else if (pb == PB_predict) {
                // std::cout << "a4" << std::endl;
            
            for (size_t i = 1; i < n; i += 2) {
                // std::cout << "a2" << std::endl;

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // std::cout << "a5" << std::endl;
                
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), .5, .5));
                // training_sampler = (training_sampler + 1) % 7;
                // if(training_sampler == 1) {
                    // a = {*(d - stride), *(d + stride)};
                    // accumulateOneSample(a, b, M, v, 2);
                    x_s.push_back({*(d - stride) * 1.0, *(d + stride) * 1.0, x * 1.0, y * 1.0, z * 1.0});
                    // x_s.push_back({*(d - stride), *(d + stride), i / 32.0, log2(stride)});
                    y_s.push_back(*d);
                // } else {
                //     continue;
                // }
                // std::cout << "a6" << std::endl;

            }
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // } else {
            //     std::cout << "waa" << std::endl;
            // }
            for (size_t i = 1; i < n; i += 2) {
                T *d = data + begin + i * stride;
                // recover(d - data, *d, interp_linear_4(*(d - stride) * 1.0, *(d + stride) * 1.0, i / 32.0, log2(stride), params[0], params[1], params[2], params[3]));
                // recover(d - data, *d, interp_linear_3(*(d - stride) * 1.0, *(d + stride) * 1.0, 1.0, params[0], params[1], params[2]));
                // recover(d - data, *d, interp_linear(*(d - stride), *(d + stride), params[0], params[1]));
                // recover(d - data, *d, interp_linear(*(d - stride), *(d + stride), .5, .5));
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                recover(d - data, *d, interp_linear_6(*(d - stride) * 1.0, *(d + stride) * 1.0, x*1.0, y*1.0, z*1.0, 1.0, params[0], params[1], params[2], params[3], params[4], params[5]));

            }
            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                if (n < 4) {
                    recover(d - data, *d, *(d - stride));
                }
            }
        }
                // std::cout << "a7" << std::endl;
        

        return predict_error;
    }
    

    double block_interpolation_1d(T *data, size_t begin, size_t end, size_t stride, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        
        size_t n = (end - begin) / stride + 1;
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << " n=" << n<< std::endl;
        // }
        if (n <= 1) {
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            // std::cout << "a1" << std::endl;

            for (size_t i = 1; i + 1 < n; i += 2) {
                // std::cout << "a2" << std::endl;

                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                // quantize(d - data, *d, interp_linear_3(*(d - stride) * 1.0, *(d + stride) * 1.0, 1.0, params[0], params[1], params[2]));
                // quantize(d - data, *d, interp_linear_4(*(d - stride) * 1.0, *(d + stride) * 1.0, i / 32.0, log2(stride), params[0], params[1], params[2], params[3]));
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                quantize(d - data, *d, interp_linear_6(*(d - stride) * 1.0, *(d + stride) * 1.0, x*1.0, y*1.0, z*1.0, 1.0, params[0], params[1], params[2], params[3], params[4], params[5]));

            }
                // std::cout << "a3" << std::endl;

            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;

                if (n < 4) {
                    // std::cout << "n=2\n" << std::endl;
                    quantize(d - data, *d, *(d - stride));
                } else {
                    quantize(d - data, *d, interp_linear1(*(d - stride * 3), *(d - stride)));
                }
            }
        } else if (pb == PB_predict) {
                // std::cout << "a4" << std::endl;
            
            for (size_t i = 1; i + 1 < n; i += 2) {
                // std::cout << "a2" << std::endl;

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // std::cout << "a5" << std::endl;
                
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), .5, .5));
                // training_sampler = (training_sampler + 1) % 7;
                // if(training_sampler == 1) {
                    // a = {*(d - stride), *(d + stride)};
                    // accumulateOneSample(a, b, M, v, 2);
                    x_s.push_back({*(d - stride) * 1.0, *(d + stride) * 1.0, x * 1.0, y * 1.0, z * 1.0});
                    // x_s.push_back({*(d - stride), *(d + stride), i / 32.0, log2(stride)});
                    y_s.push_back(*d);
                // } else {
                //     continue;
                // }
                // std::cout << "a6" << std::endl;

            }
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // } else {
            //     std::cout << "waa" << std::endl;
            // }
            for (size_t i = 1; i + 1 < n; i += 2) {
                T *d = data + begin + i * stride;
                // recover(d - data, *d, interp_linear_4(*(d - stride) * 1.0, *(d + stride) * 1.0, i / 32.0, log2(stride), params[0], params[1], params[2], params[3]));
                // recover(d - data, *d, interp_linear_3(*(d - stride) * 1.0, *(d + stride) * 1.0, 1.0, params[0], params[1], params[2]));
                // recover(d - data, *d, interp_linear(*(d - stride), *(d + stride), params[0], params[1]));
                // recover(d - data, *d, interp_linear(*(d - stride), *(d + stride), .5, .5));
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                recover(d - data, *d, interp_linear_6(*(d - stride) * 1.0, *(d + stride) * 1.0, x*1.0, y*1.0, z*1.0, 1.0, params[0], params[1], params[2], params[3], params[4], params[5]));

            }
            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                if (n < 4) {
                    recover(d - data, *d, *(d - stride));
                } else {
                    recover(d - data, *d, interp_linear1(*(d - stride * 3), *(d - stride)));
                }
            }
        }
                // std::cout << "a7" << std::endl;
        

        return predict_error;
    }
    double block_interpolation_1d_odd(T *data, size_t begin, size_t end, size_t stride, const std::string &interp_func,
                                  const PredictorBehavior pb, bool pred_first) {
        
        size_t n = (end - begin) / stride + 1;
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << " n=" << n<< std::endl;
        // }
        if (n <= 1) {
            std::cout << "waa: block_interpolation_1d_odd" << std::endl;
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            // std::cout << "a1" << std::endl;
            if(pred_first) {
                T *d = data + begin;
                quantize(d - data, *d, *(d + stride));
            }

            for (size_t i = 2; i < n - 1; i += 2) {
                // std::cout << "a2" << std::endl;

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), params[0], params[1]));
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), 0.5, 0.5));
                quantize(d - data, *d, interp_linear_6(*(d - stride) * 1.0, *(d + stride) * 1.0, x*1.0, y*1.0, z*1.0, 1.0, params[0], params[1], params[2], params[3], params[4], params[5]));
                // quantize(d - data, *d, interp_linear_4(*(d - stride) * 1.0, *(d + stride) * 1.0, i / 32.0, log2(stride), params[0], params[1], params[2], params[3]));
            }
                // std::cout << "a3" << std::endl;

            if (n % 2 == 1) {
                T *d = data + begin + (n - 1) * stride;
                // std::cout << "a4" << std::endl;
                quantize(d - data, *d, *(d - stride));
            }
        } else if (pb == PB_predict) {
            for (size_t i = 2; i < n - 1; i += 2) {
                // std::cout << "a2" << std::endl;

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];

                x_s.push_back({*(d - stride) * 1.0, *(d + stride) * 1.0, x * 1.0, y * 1.0, z * 1.0});
                y_s.push_back(*d);


            }
        } else {
            if(pred_first) {
                T *d = data + begin;
                recover(d - data, *d, *(d + stride));
            }

            for (size_t i = 2; i < n - 1; i += 2) {
                // std::cout << "a2" << std::endl;

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), params[0], params[1]));
                recover(d - data, *d, interp_linear_6(*(d - stride) * 1.0, *(d + stride) * 1.0, x*1.0, y*1.0, z*1.0, 1.0, params[0], params[1], params[2], params[3], params[4], params[5]));
                // quantize(d - data, *d, interp_linear_4(*(d - stride) * 1.0, *(d + stride) * 1.0, i / 32.0, log2(stride), params[0], params[1], params[2], params[3]));
            }
                // std::cout << "a3" << std::endl;

            if (n % 2 == 1) {
                T *d = data + begin + (n - 1) * stride;
                // std::cout << "a4" << std::endl;
                recover(d - data, *d, *(d - stride));
            }
        }
        

        return predict_error;
    }
    

    double interpolation_41x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                break;
            case 1:
                order = {0, 2, 1};
                break;
            case 2:
                order = {0, 1, 2};
                break;
            
            default:
                break;
            }
        }
        double predict_error = 0;

        M.resize(2*2, 0);
        v.resize(2, 0);
        x_s.clear();y_s.clear();
        training_sampler = 0;
        

        for (size_t i = (begin_real[order[0]] ? begin_real[order[0]] + strides[order[0]] : 0); i <= end_real[order[0]]; i += strides[order[0]]) {
            for (size_t j = (begin_real[order[1]] ? begin_real[order[1]] + strides[order[1]] : 0); j <= end_real[order[1]]; j += strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                // std::cout << "41x\n" << std::endl;

                predict_error += block_interpolation_1d(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], interp_func, pb);
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        // params = solveWithRegularization(M, v, 2, 1e-6);


        return predict_error;
    }
    double interpolation_22x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        // std::cout << "dir=" << dir << std::endl;

        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                // std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                // std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                // std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }
        x_s.clear();y_s.clear();
        training_sampler = 0;
        double predict_error = 0;
        // std::cout << "f33" << std::endl;
        for (size_t i = begin_real[order[0]] + strides[order[0]]; i <= end_real[order[0]]; i += 2 * strides[order[0]]) {
            for (size_t j = begin_real[order[1]] + strides[order[1]]; j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                if(i + strides[order[0]] >= global_dimensions[order[0]]) {
                    if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                        // std::cout << "corner2" << std::endl;
                        predict_error += block_interpolation_2d_22_corner2(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    } else {
                        // std::cout << "corner11" << std::endl;

                        predict_error += block_interpolation_2d_22_corner1(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    }
                } else if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                        // std::cout << "corner12" << std::endl;
                    predict_error += block_interpolation_2d_22_corner1(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb, !bool(begin_real[order[2]]));
                } else {
                    // std::cout << "mid" << std::endl;
                    predict_error += block_interpolation_2d_22(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                }
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        return predict_error;
    }
    double interpolation_23x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                // std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                // std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                // std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }

        x_s.clear();y_s.clear();
        training_sampler = 0;

        double predict_error = 0;
        int cnt_i = 0;
        if(begin_real[order[0]]) cnt_i++;
        for (size_t i = (begin_real[order[0]] ? begin_real[order[0]] + strides[order[0]] : 0); i <= end_real[order[0]]; i += strides[order[0]], cnt_i++) {
            bool even_i = (cnt_i % 2 == 0);
            for (size_t j = ((even_i)? begin_real[order[1]] + strides[order[1]] : (begin_real[order[1]] ? begin_real[order[1]] + 2 * strides[order[1]] : 0)); j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];

                if(i == 0) {
                    if(begin_real[order[0]]) {continue; }
                    else {
                        if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                            // top left corner
                            // std::cout << "top left corner" << std::endl;
                            
                            predict_error += block_interpolation_2d_23_corner(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], -strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                        } else {
                            // left edge
                            // std::cout << "left edge" << std::endl;

                            predict_error += block_interpolation_2d_23_edge(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));

                        }
                    }
                } else if(i + strides[order[0]] >= global_dimensions[order[0]]) {
                    if(j == 0) {
                        // bot right corner
                        // std::cout << "bot right corner" << std::endl;
                        
                        predict_error += block_interpolation_2d_23_corner(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], -strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    } else if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                        // top right corner
                        // std::cout << "top right corner" << std::endl;
                        // std::cout << "stride = " << strides[order[1]] << " begin = " << begin_real[order[1]] << " end=" <<end_real[order[1]] << " cnt_i = " << cnt_i << " even_i" << even_i << std::endl;
                        // std::cout << "begin x = " << begin_real[order[0]] << " j=" << j << std::endl;
                        predict_error += block_interpolation_2d_23_corner(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    } else {
                        // right edge
                        // std::cout << "right edge" << std::endl;

                        predict_error += block_interpolation_2d_23_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    }
                } else if(j == 0) {
                    // bot edge
                    // std::cout << "bot edge" << std::endl;
                    
                    predict_error += block_interpolation_2d_23_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb, !bool(begin_real[order[2]]));
                } else if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                    // top edge
                    // std::cout << "top edge" << std::endl;
                    // std::cout << "stride = " << strides[order[1]] << " begin = " << begin_real[order[1]] << " end=" <<end_real[order[1]] << " cnt_i = " << cnt_i << " even_i" << even_i << std::endl;
                    // std::cout << "begin x = " << begin_real[order[0]] << " j=" << j << std::endl;
                    predict_error += block_interpolation_2d_23_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb, !bool(begin_real[order[2]]));
                } else {
                    // std::cout << "mid" << std::endl;
                    predict_error += block_interpolation_2d_23(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                }
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        return predict_error;
    }
    
    double interpolation_42x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // std::cout << "42x: " << "br = " << begin_real[dir] << " er = " << end_real[dir] << " stride = " << strides[dir] << std::endl;
        // begin_real[dir] = begin_real[dir]/2;
        // end_real[dir] = end_real[dir]/2;
        strides[dir] = strides[dir] * 2;
        return interpolation_23x(data, begin_real, end_real, strides, dir, interp_func, pb);
    }

    double interpolation_25x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                break;
            case 1:
                order = {0, 2, 1};
                break;
            case 2:
                order = {0, 1, 2};
                break;
            
            default:
                break;
            }
        }
        double predict_error = 0;

        M.resize(2*2, 0);
        v.resize(2, 0);
        x_s.clear();y_s.clear();
        training_sampler = 0;

        for (size_t i = begin_real[order[0]] + strides[order[0]]; i <= end_real[order[0]]; i += 2 * strides[order[0]]) {
            for (size_t j = begin_real[order[1]] + strides[order[1]]; j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                // std::cout << "41x\n" << std::endl;

                predict_error += block_interpolation_1d(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], interp_func, pb);
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        for (size_t i = (begin_real[order[0]] ? begin_real[order[0]] + 2 * strides[order[0]] : 0); i <= end_real[order[0]]; i += 2 * strides[order[0]]) {
            for (size_t j = (begin_real[order[1]] ? begin_real[order[1]] + 2 * strides[order[1]] : 0); j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                // std::cout << "41x\n" << std::endl;

                predict_error += block_interpolation_1d(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], interp_func, pb);
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        // params = solveWithRegularization(M, v, 2, 1e-6);


        return predict_error;
    }
    double interpolation_24x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                // std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                // std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                // std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }
        x_s.clear();y_s.clear();
        training_sampler = 0;

        double predict_error = 0;
        int cnt_i = 0;
        if(begin_real[order[0]]) cnt_i++;
        for (size_t i = (begin_real[order[0]] ? begin_real[order[0]] + strides[order[0]] : 0); i <= end_real[order[0]]; i += strides[order[0]], cnt_i++) {
            bool even_i = (cnt_i % 2 == 0);
            for (size_t j = ((even_i)? begin_real[order[1]] + strides[order[1]] : (begin_real[order[1]] ? begin_real[order[1]] + 2 * strides[order[1]] : 0)); j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];

                if(i == 0) {
                    if(begin_real[order[0]]) {continue; }
                    else {
                        if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                            // top left corner
                            // std::cout << "top left corner" << std::endl;
                            
                            predict_error += block_interpolation_2d_24_corner(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], -strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                        } else {
                            // left edge
                            // std::cout << "left edge" << std::endl;

                            predict_error += block_interpolation_2d_24_edge(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);

                        }
                    }
                } else if(i + strides[order[0]] >= global_dimensions[order[0]]) {
                    if(j == 0) {
                        // bot right corner
                        // std::cout << "bot right corner" << std::endl;
                        
                        predict_error += block_interpolation_2d_24_corner(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], -strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                    } else if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                        // top right corner
                        // std::cout << "top right corner" << std::endl;
                        // std::cout << "stride = " << strides[order[1]] << " begin = " << begin_real[order[1]] << " end=" <<end_real[order[1]] << " cnt_i = " << cnt_i << " even_i" << even_i << std::endl;
                        // std::cout << "begin x = " << begin_real[order[0]] << " j=" << j << std::endl;
                        predict_error += block_interpolation_2d_24_corner(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                    } else {
                        // right edge
                        // std::cout << "right edge" << std::endl;

                        predict_error += block_interpolation_2d_24_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                    }
                } else if(j == 0) {
                    // bot edge
                    // std::cout << "bot edge" << std::endl;
                    
                    predict_error += block_interpolation_2d_24_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb);
                } else if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                    // top edge
                    // std::cout << "top edge" << std::endl;
                    // std::cout << "stride = " << strides[order[1]] << " begin = " << begin_real[order[1]] << " end=" <<end_real[order[1]] << " cnt_i = " << cnt_i << " even_i" << even_i << std::endl;
                    // std::cout << "begin x = " << begin_real[order[0]] << " j=" << j << std::endl;
                    predict_error += block_interpolation_2d_24_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb);
                } else {
                    // std::cout << "mid" << std::endl;
                    predict_error += block_interpolation_2d_24(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                }
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        return predict_error;
    }

    double interpolation_12x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // std::cout << "12x: " << "br = " << begin_real[dir] << " er = " << end_real[dir] << " stride = " << strides[dir] << std::endl;
        // begin_real[dir] = begin_real[dir]/2;
        // end_real[dir] = end_real[dir]/2;
        strides[dir] = strides[dir] * 2;
        return interpolation_22x(data, begin_real, end_real, strides, dir, interp_func, pb);
    }
    
    double interpolation_43x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        // std::cout << "dir=" << dir << std::endl;

        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                // std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                // std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                // std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }

        x_s.clear();y_s.clear();
        training_sampler = 0;

        double predict_error = 0;
        // std::cout << "43x:" << std::endl;
        // int cnt = (begin_real[order[0]] ? 1 : 0) + (begin_real[order[1]] ? 1 : 0);

        for (size_t i = (begin_real[order[0]] ? begin_real[order[0]] + strides[order[0]] : 0); i <= end_real[order[0]]; i += strides[order[0]]) {
            for (size_t j = (begin_real[order[1]] ? begin_real[order[1]] + strides[order[1]] : 0); j <= end_real[order[1]]; j += strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                int cnti = (strides[order[0]] ? (i - begin_real[order[0]]) / strides[order[0]] : 0);
                int cntj = (strides[order[1]] ? (j - begin_real[order[1]]) / strides[order[1]] : 0);
                if(((cnti % 2) + cntj) % 2 == 0) {
                    // std::cout << "even i: " << (strides[order[0]] ? (i - begin_real[order[0]]) / strides[order[0]] : 0) << " j: " << (strides[order[1]] ? (j - begin_real[order[1]]) / strides[order[1]] : 0) << std::endl;
                    predict_error += block_interpolation_3d_43(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]],
                                interp_func, pb, false, false, strides[0], strides[1], strides[2]);
                } else {
                    // std::cout << "odd i: " << (strides[order[0]] ? (i - begin_real[order[0]]) / strides[order[0]] : 0) << " j: " << (strides[order[1]] ? (j - begin_real[order[1]]) / strides[order[1]] : 0) << std::endl;
                    // predict_error += block_interpolation_1d_odd(
                    //             data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                    //             strides[order[2]] * dimension_offsets[order[2]], interp_func, pb, begin_real[order[2]] == 0);
                    predict_error += block_interpolation_3d_43(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]],
                                interp_func, pb, true, begin_real[order[2]] != 0, strides[0], strides[1], strides[2]);
                }
                    // std::cout << "quant_index: " << quant_index << std::endl;
                        
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        return predict_error;
    }

    double interpolation_13x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        // std::cout << "dir=" << dir << std::endl;

        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                // std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                // std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                // std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }

        x_s.clear();y_s.clear();
        training_sampler = 0;

        double predict_error = 0;
        for (size_t i = begin_real[order[0]] + strides[order[0]]; i <= end_real[order[0]]; i += 2 * strides[order[0]]) {
            for (size_t j = begin_real[order[1]] + strides[order[1]]; j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                if(i + strides[order[0]] >= global_dimensions[order[0]]) {
                    if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                        // std::cout << "13 top right corner" << std::endl;
                        predict_error += block_interpolation_2d_13_corner(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                    } else {
                        // std::cout << "13 right edge" << std::endl;

                        predict_error += block_interpolation_2d_13_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                    }
                } else if(j + strides[order[1]] >= global_dimensions[order[1]]) {
                        // std::cout << "13 top edge" << std::endl;
                    predict_error += block_interpolation_2d_13_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb);
                } else {
                    // std::cout << "mid" << std::endl;
                    predict_error += block_interpolation_2d_13(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb);
                }
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }
        return predict_error;
    }
    double interpolation_26x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        // std::cout << "dir=" << dir << std::endl;

        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                // std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                // std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                // std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }
        double predict_error = 0;
        // std::cout << "26x:" << std::endl;
        // int cnt = (begin_real[order[0]] ? 1 : 0) + (begin_real[order[1]] ? 1 : 0);
        x_s.clear();y_s.clear();
        training_sampler = 0;
        
        for (size_t i = (begin_real[order[0]] ? begin_real[order[0]] + 2 * strides[order[0]] : 0); i <= end_real[order[0]]; i += 2 * strides[order[0]]) {
            for (size_t j = (begin_real[order[1]] ? begin_real[order[1]] + 2 * strides[order[1]] : 0); j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                predict_error += block_interpolation_1d(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], interp_func, pb);
                
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }

        for (size_t i = begin_real[order[0]] + strides[order[0]]; i <= end_real[order[0]]; i += 2 * strides[order[0]]) {
            for (size_t j = begin_real[order[1]] + strides[order[1]]; j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                predict_error += block_interpolation_1d_odd(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], interp_func, pb, begin_real[order[2]] == 0);
                if(strides[order[1]] == 0) break;
            }
            if(strides[order[0]] == 0) break;
        }

        return predict_error;
    }

    double interpolation(T *data, std::array<int, 3> begin,
                        std::array<int, 3> end,
                        const PredictorBehavior pb,
                        const std::string &interp_func,
                        int action, std::array<int, 3> strides, int dir) {
        // double predict_error = 0;
        // size_t stride2x = stride * 2;
        // const std::array<int, N> dims = dimension_sequences[direction];
        // std::cout << "interp " << "begin: " << begin[0] <<' '<<begin[1]<<' '<<begin[2] <<",end: " << end[0]<<' '<<end[1]<<' '<<end[2]<<std::endl;
        // std::cout << "interp " << "stride: " << strides[0] <<' '<<strides[1]<<' '<<strides[2] <<" dir=" << dir << " action:" <<action<<std::endl;
        std::array<int, 3> begin_real, end_real;
        for(int i = 0; i < 3; i++) {
            begin_real[i] = begin[i] * strides[i];
            end_real[i] = end[i] * strides[i];
        }
        // std::cout << "interp " << "begin_real: " << begin_real[0] <<' '<<begin_real[1]<<' '<<begin_real[2] <<",end_real: " << end_real[0]<<' '<<end_real[1]<<' '<<end_real[2]<<std::endl;

            // std::cout << "f16\n" << std::endl;
        if(action > 430) {
            // std::cout << "f41\n" << std::endl;

            return interpolation_43x(data, begin_real, end_real, strides,dir, interp_func, pb);
            // coeff_idx++;
        } else if(action > 420) {
            // std::cout << "f41\n" << std::endl;
            return interpolation_42x(data, begin_real, end_real, strides,dir, interp_func, pb);
            // coeff_idx++;
        } else if(action > 400) {
            return interpolation_41x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else if(action > 260) {
            return interpolation_26x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else if(action > 250) {
            return interpolation_25x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else if(action > 240) {
            return interpolation_24x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else if(action > 230) {
            return interpolation_23x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else if(action > 200) {
            return interpolation_22x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else if(action > 130) {
            return interpolation_13x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else {
            return interpolation_12x(data, begin_real, end_real, strides,dir, interp_func, pb);
            // std::cout << "f22\n" << std::endl;
        }
    }


    int interpolation_level = -1;
    uint blocksize;
    int interpolator_id;
    double eb_ratio = 0.5;
    std::vector<std::string> interpolators = {"linear", "cubic"};
    int *quant_inds;
    size_t quant_index = 0;
    double max_error;
    Quantizer quantizer;
    size_t num_elements;
    std::array<size_t, N> global_dimensions;
    std::array<size_t, N> dimension_offsets;
    std::vector<std::array<int, N>> dimension_sequences;
    int direction_sequence_id;

    enum state {A, B, C, D, E, F, G, Z};
    // coeff
    std::vector<double> M;
    std::vector<double> v;
    std::vector<double> params;
    std::vector<std::vector<_Float32>> coeff_list;
    size_t coeff_idx = 0;
    std::vector<std::array<int, 4>> level_dimensions;
    std::vector<std::vector<double>> x_s;
    std::vector<double> y_s;
    int training_sampler = 0;
    double filter_threshold = 3.0;
    double lambda = 1e-7;

    //normalization
    double norm_min = 0;
    double norm_max = 0;

    char* tpPath = nullptr;

    double block_interpolation_2d_22(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb, bool startfrombot) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;

        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});
        // std::cout << "n=" << n << " begin=" << begin << " end=" << end << " stride=" << stride << " p1=" << stride_p1 << " p2=" << stride_p2<< std::endl;

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            if (startfrombot) {
                T *d = data + begin;
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2), *(d + stride_p1 - stride_p2), *(d + stride_p1 + stride_p2)));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2), *(d + stride_p1 - stride_p2), *(d + stride_p1 + stride_p2)));
            }
            
                
        } else if(pb == PB_predict) {
            
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            if (startfrombot) {
                T *d = data + begin;
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2), *(d + stride_p1 - stride_p2), *(d + stride_p1 + stride_p2)));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2), *(d + stride_p1 - stride_p2), *(d + stride_p1 + stride_p2)));
            }
        }
        

        return predict_error;
    }
    double block_interpolation_2d_22_corner1(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb, bool startfrombot) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;

        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            if (startfrombot) {
                T *d = data + begin;
                quantize(d - data, *d, interp_linear_2d_22x_corner1(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2)));
            }
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                
                quantize(d - data, *d, interp_linear_2d_22x_corner1(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2)));
            }
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            if (startfrombot) {
                T *d = data + begin;
                recover(d - data, *d, interp_linear_2d_22x_corner1(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2)));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_2d_22x_corner1(*(d - stride_p1 - stride_p2), *(d - stride_p1 + stride_p2)));
            }
        }
        

        return predict_error;
    }
    
    double block_interpolation_2d_22_corner2(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb, bool startfrombot) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            if (startfrombot) {
                T *d = data + begin;
                quantize(d - data, *d, interp_linear_2d_22x_corner2(*(d - stride_p1 - stride_p2)));
            }
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_2d_22x_corner2(*(d - stride_p1 - stride_p2)));
            }
        
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            if (startfrombot) {
                T *d = data + begin;
                recover(d - data, *d, interp_linear_2d_22x_corner2(*(d - stride_p1 - stride_p2)));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_2d_22x_corner2(*(d - stride_p1 - stride_p2)));
            }
        }
        

        return predict_error;
    }
    
    double block_interpolation_2d_23(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb, bool startfrombot) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;

        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            if (startfrombot) {
                T *d = data + begin;
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1), *(d + stride_p1), *(d - stride_p2), *(d + stride_p2)));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_8(*(d - stride_p1) * 1.0, *(d + stride_p1) * 1.0, *(d - stride_p2) * 1.0, *(d + stride_p2) * 1.0,
                                                        x * 1.0, y * 1.0, z * 1.0, 1.0,
                                                        params[0], params[1], params[2], params[3], 
                                                        params[4], params[5], params[6], params[7]));
            }
        } else if(pb == PB_predict) {
            for (size_t i = 1; i < n; i++) {

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                x_s.push_back({*(d - stride_p1) * 1.0, *(d + stride_p1) * 1.0, *(d - stride_p2) * 1.0, *(d + stride_p2) * 1.0,
                                x * 1.0, y * 1.0, z * 1.0});
                y_s.push_back(*d);
            }
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            if (startfrombot) {
                T *d = data + begin;
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1), *(d + stride_p1), *(d - stride_p2), *(d + stride_p2)));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_8(*(d - stride_p1) * 1.0, *(d + stride_p1) * 1.0, *(d - stride_p2) * 1.0, *(d + stride_p2) * 1.0,
                                                        x * 1.0, y * 1.0, z * 1.0, 1.0,
                                                        params[0], params[1], params[2], params[3], 
                                                        params[4], params[5], params[6], params[7]));
                }
        }
        

        return predict_error;
    }
    double block_interpolation_2d_23_edge(T *data, size_t begin, size_t end, size_t stride, int stride_p1, const std::string &interp_func,
                                  const PredictorBehavior pb, bool startfrombot) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});
        // std::cout << "n=" << n << " begin=" << begin << " end=" << end << " stride=" << stride << " p1=" << stride_p1 << std::endl;

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            if (startfrombot) {
                T *d = data + begin;
                quantize(d - data, *d, interp_linear(*(d - stride_p1), *(d + stride_p1), .5, .5));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear(*(d - stride_p1), *(d + stride_p1), .5, .5));
            }
        } else if(pb == PB_predict) {

        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            if (startfrombot) {
                T *d = data + begin;
                recover(d - data, *d, interp_linear(*(d - stride_p1), *(d + stride_p1), .5, .5));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear(*(d - stride_p1), *(d + stride_p1), .5, .5));
            }
        }
        

        return predict_error;
    }
    
    double block_interpolation_2d_23_corner(T *data, size_t begin, size_t end, size_t stride, int stride_p1, int stride_p2, const std::string &interp_func,
                                    const PredictorBehavior pb, bool startfrombot) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});


        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            if (startfrombot) {
                T *d = data + begin;
                quantize(d - data, *d, interp_linear(*(d - stride_p1), *(d - stride_p2), .5, .5));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear(*(d - stride_p1), *(d - stride_p2), .5, .5));
            }
        } else if(pb == PB_predict) {

        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            if (startfrombot) {
                T *d = data + begin;
                recover(d - data, *d, interp_linear(*(d - stride_p1), *(d - stride_p2), .5, .5));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear(*(d - stride_p1), *(d - stride_p2), .5, .5));
            }
        }


        return predict_error;
    }
    double block_interpolation_2d_24(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        if(n <= 1) {
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            
            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_12(*(d - stride_p1 - stride) * 1.0, *(d + stride_p1 - stride) * 1.0, *(d - stride_p2 - stride) * 1.0, *(d + stride_p2 - stride) * 1.0,
                                                            *(d - stride_p1 + stride) * 1.0, *(d + stride_p1 + stride) * 1.0, *(d - stride_p2 + stride) * 1.0, *(d + stride_p2 + stride) * 1.0, 
                                                            x * 1.0, y * 1.0, z * 1.0, 1.0, 
                                                            params[0], params[1], params[2], params[3],
                                                            params[4], params[5], params[6], params[7],
                                                            params[8], params[9], params[10], params[11]));
            }
            if(n % 2 == 0) { // even
                T *d = data + begin + (n - 1) * stride;
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride), *(d + stride_p1 - stride), *(d - stride_p2 - stride), *(d + stride_p2 - stride)));
            }   
            
        } else if(pb == PB_predict) {
            for (size_t i = 1; i < n - 1; i+=2) {

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                x_s.push_back({*(d - stride_p1 - stride) * 1.0, *(d + stride_p1 - stride) * 1.0, *(d - stride_p2 - stride) * 1.0, *(d + stride_p2 - stride) * 1.0,
                                *(d - stride_p1 + stride) * 1.0, *(d + stride_p1 + stride) * 1.0, *(d - stride_p2 + stride) * 1.0, *(d + stride_p2 + stride) * 1.0,
                                x * 1.0, y * 1.0, z * 1.0});
                y_s.push_back(*d);
            }
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_12(*(d - stride_p1 - stride) * 1.0, *(d + stride_p1 - stride) * 1.0, *(d - stride_p2 - stride) * 1.0, *(d + stride_p2 - stride) * 1.0,
                                                            *(d - stride_p1 + stride) * 1.0, *(d + stride_p1 + stride) * 1.0, *(d - stride_p2 + stride) * 1.0, *(d + stride_p2 + stride) * 1.0, 
                                                            x * 1.0, y * 1.0, z * 1.0, 1.0, 
                                                            params[0], params[1], params[2], params[3],
                                                            params[4], params[5], params[6], params[7],
                                                            params[8], params[9], params[10], params[11]));
            }
            if(n % 2 == 0) { // even
                T *d = data + begin + (n - 1) * stride;
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride), *(d + stride_p1 - stride), *(d - stride_p2 - stride), *(d + stride_p2 - stride)));
            }  
        }
        

        return predict_error;
    }
    double block_interpolation_2d_24_corner(T *data, size_t begin, size_t end, size_t stride, int stride_p1, int stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        if(n <= 1) {
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});
        // std::cout << "n=" << n << " begin=" << begin << " end=" << end << " stride=" << stride << " p1=" << stride_p1 << std::endl;

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            for (size_t i = 1; i < n; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear(*(d - stride_p1 - stride), *(d - stride_p2 - stride), .5, .5));
            }
            // if(n % 2 == 0) { // even
            //     T *d = data + begin + (n - 1) * stride;
            //     quantize(d - data, *d, interp_linear(*(d - stride_p1 - stride), *(d - stride_p2 - stride), .5, .5));
            // } 
        } else if(pb == PB_predict) {

        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;
            for (size_t i = 1; i < n; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear(*(d - stride_p1 - stride), *(d - stride_p2 - stride), .5, .5));
            }
            // if(n % 2 == 0) { // even
            //     T *d = data + begin + (n - 1) * stride;
            //     recover(d - data, *d, interp_linear(*(d - stride_p1 - stride), *(d - stride_p2 - stride), .5, .5));
            // } 
        }
        

        return predict_error;
    }
    
    double block_interpolation_2d_24_edge(T *data, size_t begin, size_t end, size_t stride, int stride_p1, const std::string &interp_func,
                                    const PredictorBehavior pb) {

                                        
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        if(n <= 1) {
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        // std::cout << "f1" << std::endl;
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride), *(d + stride_p1 - stride), *(d - stride_p1 + stride), *(d + stride_p1 + stride)));
            }
            if(n % 2 == 0) { // even
                T *d = data + begin + (n - 1) * stride;
                quantize(d - data, *d, interp_linear(*(d - stride_p1 - stride), *(d + stride_p1 - stride), 0.5, 0.5));
            }   
        } else if(pb == PB_predict) {

        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            // coeff_idx++;

            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride), *(d + stride_p1 - stride), *(d - stride_p1 + stride), *(d + stride_p1 + stride)));
            }

            if(n % 2 == 0) { // even
                T *d = data + begin + (n - 1) * stride;
                recover(d - data, *d, interp_linear(*(d - stride_p1 - stride), *(d + stride_p1 - stride), 0.5, 0.5));
            }   
        
        }


        return predict_error;
    }
    double block_interpolation_2d_13(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        if(n <= 1) {
            return 0;
        }

        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});
        // std::cout << "n=" << n << " begin=" << begin << " end=" << end << " stride=" << stride << " p1=" << stride_p1 << " p2=" << stride_p2<< std::endl;

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;

            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_12(*(d - stride_p1 - stride_p2 - stride) * 1.0, *(d - stride_p1 + stride_p2 - stride) * 1.0, *(d + stride_p1 - stride_p2 - stride) * 1.0, *(d + stride_p1 + stride_p2 - stride) * 1.0,
                                                            *(d - stride_p1 - stride_p2 + stride) * 1.0, *(d - stride_p1 + stride_p2 + stride) * 1.0, *(d + stride_p1 - stride_p2 + stride) * 1.0, *(d + stride_p1 + stride_p2 + stride) * 1.0,
                                                            x * 1.0, y * 1.0, z * 1.0, 1.0, 
                                                            params[0], params[1], params[2], params[3],
                                                            params[4], params[5], params[6], params[7],
                                                            params[8], params[9], params[10], params[11]));
                // quantize(d - data, *d, *(d - stride_p1 - stride_p2 - stride));
            }
            if(n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride_p2 - stride), *(d - stride_p1 + stride_p2 - stride), *(d + stride_p1 - stride_p2 - stride), *(d + stride_p1 + stride_p2 - stride)));
                // quantize(d - data, *d, *(d - stride_p1 - stride_p2 - stride));
            }
        } else if(pb == PB_predict) {

            for (size_t i = 1; i < n - 1; i+=2) {

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                x_s.push_back({*(d - stride_p1 - stride_p2 - stride) * 1.0, *(d - stride_p1 + stride_p2 - stride) * 1.0, *(d + stride_p1 - stride_p2 - stride) * 1.0, *(d + stride_p1 + stride_p2 - stride) * 1.0,
                                *(d - stride_p1 - stride_p2 + stride) * 1.0, *(d - stride_p1 + stride_p2 + stride) * 1.0, *(d + stride_p1 - stride_p2 + stride) * 1.0, *(d + stride_p1 + stride_p2 + stride) * 1.0,
                                x * 1.0, y * 1.0, z * 1.0});
                y_s.push_back(*d);
            }
        } else {
            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_12(*(d - stride_p1 - stride_p2 - stride) * 1.0, *(d - stride_p1 + stride_p2 - stride) * 1.0, *(d + stride_p1 - stride_p2 - stride) * 1.0, *(d + stride_p1 + stride_p2 - stride) * 1.0,
                                                            *(d - stride_p1 - stride_p2 + stride) * 1.0, *(d - stride_p1 + stride_p2 + stride) * 1.0, *(d + stride_p1 - stride_p2 + stride) * 1.0, *(d + stride_p1 + stride_p2 + stride) * 1.0,
                                                            x * 1.0, y * 1.0, z * 1.0, 1.0, 
                                                            params[0], params[1], params[2], params[3],
                                                            params[4], params[5], params[6], params[7],
                                                            params[8], params[9], params[10], params[11]));

            }
            if(n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 - stride_p2 - stride), *(d - stride_p1 + stride_p2 - stride), *(d + stride_p1 - stride_p2 - stride), *(d + stride_p1 + stride_p2 - stride)));
                // recover(d - data, *d, *(d - stride_p1 - stride_p2 - stride));
            }
        }
        

        return predict_error;
    }
    double block_interpolation_2d_13_edge(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        if(n <= 1) {
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {
            // float x0 = static_cast<float>(coeff_list.back()[0]);
            // float x1 = static_cast<float>(coeff_list.back()[1]);
            // std::cout << x0 << "   " << x1 << std::endl;
            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 + stride_p2 - stride), *(d - stride_p1 - stride_p2 - stride),
                                                            *(d - stride_p1 + stride_p2 + stride), *(d - stride_p1 - stride_p2 + stride)));
                // quantize(d - data, *d, *(d - stride_p1 - stride_p2 - stride));

            }
            if(n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                quantize(d - data, *d, interp_linear(*(d - stride_p1 + stride_p2 - stride), *(d - stride_p1 - stride_p2 - stride), 0.5, 0.5));
                // quantize(d - data, *d, *(d - stride_p1 - stride_p2 - stride));
            }
        } else if(pb == PB_predict) {

        } else {
            for (size_t i = 1; i < n - 1; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1 + stride_p2 - stride), *(d - stride_p1 - stride_p2 - stride),
                                                            *(d - stride_p1 + stride_p2 + stride), *(d - stride_p1 - stride_p2 + stride)));
                // recover(d - data, *d, *(d - stride_p1 - stride_p2 - stride));

            }
            if(n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                recover(d - data, *d, interp_linear(*(d - stride_p1 + stride_p2 - stride), *(d - stride_p1 - stride_p2 - stride), 0.5, 0.5));
                // recover(d - data, *d, *(d - stride_p1 - stride_p2 - stride));

            }
        }
        

        return predict_error;
    }
    
    double block_interpolation_2d_13_corner(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        if(n <= 1) {
            return 0;
        }
        double predict_error = 0;
        // calc_coeff(data, begin, end, stride);
        // coeff_list.push_back(std::vector<_Float32>{0.5,0.5});

        
        if (pb == PB_predict_overwrite) {

            for (size_t i = 1; i < n; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, *(d - stride_p1 - stride_p2 - stride));
            }
        } else if(pb == PB_predict) {

        } else {
            for (size_t i = 1; i < n; i+=2) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, *(d - stride_p1 - stride_p2 - stride));
            }
        }
        

        return predict_error;
    }


    double block_interpolation_3d_43(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb, bool startfrombeginning, bool skipbeginning, int stride_x, int stride_y, int stride_z) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << ", stride_p1: " << stride_p1 << ", stride_p2: " << stride_p2 << std::endl;
        // }
        size_t n = (stride == 0) ? 1 : (end - begin) / stride + 1;
        int x_0 = (begin) / dimension_offsets[0];
        int y_0 = (begin - x_0 * dimension_offsets[0]) / dimension_offsets[1];
        int z_0 = begin - x_0 * dimension_offsets[0] - y_0 * dimension_offsets[1];
        // { // Log
        //     std::cout << "[Log] x_0: " << x_0 << ", y_0: " << y_0 << ", z_0: " << z_0 << std::endl;
        // }
        if(n <= 1) {
            return 0;
        }
        // { // Log
        //     std::cout << "[Log] stride_x: " << stride_x << ", stride_y: " << stride_y << ", stride_z: " << stride_z << std::endl;
        // }

        double predict_error = 0;

        bool legal_ptop = (y_0 + stride_y < global_dimensions[1]);
        bool legal_pdown = (y_0 - stride_y >= 0);
        bool legal_pright = (x_0 + stride_x < global_dimensions[0]);
        bool legal_pleft = (x_0 - stride_x >= 0);
        bool legal_pbehind = (z_0 - stride_z >= 0);
        bool legal_pfront = (z_0 + n * stride_z < global_dimensions[2]);
        
        if (pb == PB_predict_overwrite) {
            for (size_t i = startfrombeginning ? (skipbeginning ? 2 : 0) : 1; i < n; i+=2) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));

                T top = legal_ptop ? *(d + stride_p2) : 0;
                T down = legal_pdown ? *(d - stride_p2) : 0;
                T right = legal_pright ? *(d + stride_p1) : 0;
                T left = legal_pleft ? *(d - stride_p1) : 0;
                T behind = (legal_pbehind || (i > 0)) ? *(d - stride) : 0;
                T front = (legal_pfront || i != (n - 1)) ? *(d + stride) : 0;
                // T behind = 0;
                // T front = 0;
               
                quantize(d - data, *d, interp_linear_10(
                    left * 1.0, right * 1.0, down * 1.0, top * 1.0, behind * 1.0, front * 1.0,
                    x * 1.0, y * 1.0, z * 1.0, 1.0,
                    params[0], params[1], params[2], params[3], params[4], 
                    params[5], params[6], params[7], params[8], params[9]
                ));
            }
        } else if(pb == PB_predict) {
            for (size_t i = startfrombeginning ? (skipbeginning ? 2 : 0) : 1; i < n; i+=2) {

                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));

                T top = legal_ptop ? *(d + stride_p2) : 0;
                T down = legal_pdown ? *(d - stride_p2) : 0;
                T right = legal_pright ? *(d + stride_p1) : 0;
                T left = legal_pleft ? *(d - stride_p1) : 0;
                T behind = (legal_pbehind || (i > 0)) ? *(d - stride) : 0;
                T front = (legal_pfront || i != (n - 1)) ? *(d + stride) : 0;
                if(top && down && right && left && behind && front) {
                    x_s.push_back({left * 1.0, right * 1.0, down * 1.0, top * 1.0, behind * 1.0, front * 1.0, x * 1.0, y * 1.0, z * 1.0});
                    y_s.push_back(*d);
                }
            }
        } else {
            for (size_t i = startfrombeginning ? (skipbeginning ? 2 : 0) : 1; i < n; i+=2) {
                T *d = data + begin + i * stride;
                size_t x = (begin + i * stride) / dimension_offsets[0];
                size_t y = (begin + i * stride - x * dimension_offsets[0]) / dimension_offsets[1];
                size_t z = begin + i * stride - x * dimension_offsets[0] - y * dimension_offsets[1];
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));

                T top = legal_ptop ? *(d + stride_p2) : 0;
                T down = legal_pdown ? *(d - stride_p2) : 0;
                T right = legal_pright ? *(d + stride_p1) : 0;
                T left = legal_pleft ? *(d - stride_p1) : 0;
                T behind = (legal_pbehind || (i > 0)) ? *(d - stride) : 0;
                T front = (legal_pfront || i != (n - 1)) ? *(d + stride) : 0;
                // T behind = 0;
                // T front = 0;

                recover(d - data, *d, interp_linear_10(
                    left * 1.0, right * 1.0, down * 1.0, top * 1.0, behind * 1.0, front * 1.0,
                    x * 1.0, y * 1.0, z * 1.0, 1.0,
                    params[0], params[1], params[2], params[3], params[4], 
                    params[5], params[6], params[7], params[8], params[9]
                ));
            }
        }
        

        return predict_error;
    }
    
};

template <class T, uint N, class Quantizer>
FHDEDecomposition<T, N, Quantizer> make_decomposition_FHDE(const Config &conf, Quantizer quantizer) {
    return FHDEDecomposition<T, N, Quantizer>(conf, quantizer);
}

}  // namespace FHDE

#endif