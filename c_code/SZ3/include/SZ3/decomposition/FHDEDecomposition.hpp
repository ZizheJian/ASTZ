#ifndef _SZ_INTERPOLATION_DECOMPOSITION_HPP
#define _SZ_INTERPOLATION_DECOMPOSITION_HPP

#include <cmath>
#include <cstring>

#include "Decomposition.hpp"
#include "SZ3/def.hpp"
#include "SZ3/quantizer/Quantizer.hpp"
#include "SZ3/utils/Config.hpp"
#include "SZ3/utils/FileUtil.hpp"
#include "SZ3/utils/Interpolators.hpp"
#include "SZ3/utils/Iterator.hpp"
#include "SZ3/utils/MemoryUtil.hpp"
#include "SZ3/utils/Timer.hpp"

namespace SZ3 {
template <class T, uint N, class Quantizer>
class FHDEDecomposition : public concepts::DecompositionInterface<T, int, N> {
   public:
    FHDEDecomposition(const Config &conf, Quantizer quantizer) : quantizer(quantizer) {
        static_assert(std::is_base_of<concepts::QuantizerInterface<T, int>, Quantizer>::value,
                      "must implement the quantizer interface");
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
        for (uint level = interpolation_level - 1; level >= 0 && level < interpolation_level; level--) {
            if (level >= 3) {
                quantizer.set_eb(eb * eb_ratio);
            } else {
                quantizer.set_eb(eb);
            }
            
            { // Log
                std::cout << level << std::endl;
            }
            // size_t stride = 1U << (level - 1);

            std::array<int, 3> strides = calc_stride(level_dimensions[level]);
            int dir = 0;
            int dir2 = 0;
            bool foundone = false;
            bool foundtwo = false;
            { // predict behavier
                
                for(int i = 0; i < 3; i++) {
                    if(level_dimensions[level][i] > last_dim[i]){
                        
                        if(foundone) {
                            dir2 = i;
                            foundtwo = true;
                        } else {
                            dir = i;
                        }
                        foundone = true;
                    }
                }
                // int last_digit = (level_dimensions[level][3] % 10);
                // switch (last_digit)
                // {
                // case 1:
                //     dir = 2;
                //     break;
                // case 2:
                //     dir = 1;
                //     break;
                // case 3:
                //     dir = 0;
                //     break;
                // default:
                //     break;
                // }
                last_dim = level_dimensions[level];
            }
            
            std::vector<std::array<int, 3>> begins, ends;
            std::cout << level_dimensions[level][0] << ' ' << level_dimensions[level][1] << ' ' << level_dimensions[level][2] << std::endl;
            block_divider(level_dimensions[level], begins, ends);
            // std::cout << begins.size() << ' ' << ends.size() << std::endl;
            if(foundtwo) dir = 3 - dir - dir2;

            for(int i = 0; i < begins.size(); i++) {
                // std::cout << "block" << i << ": " << begins[i][0] << ' ' << begins[i][1] << ' ' << begins[i][2] << " to " << ends[i][0] << ' ' << ends[i][1] << ' ' << ends[i][2] << std::endl;
                if(foundtwo) {
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 221, strides, dir);
                } else if (foundone) {
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 411, strides, dir);
                } else {
                    interpolation(dec_data, begins[i], ends[i], PB_recover, interpolators[interpolator_id], 111, strides, last_dir);
                }
                // { // Log
                //     std::cout << "quant_index: " << quant_index << std::endl;
                // }
            }
            last_dir = dir;

        }

        // for (uint level = interpolation_level; level > 0 && level <= interpolation_level; level--) {
            // if (level >= 3) {
            //     quantizer.set_eb(eb * eb_ratio);
            // } else {
            //     quantizer.set_eb(eb);
            // }


            // size_t stride = 1U << (level - 1);
            // auto inter_block_range = std::make_shared<multi_dimensional_range<T, N>>(
            //     dec_data, std::begin(global_dimensions), std::end(global_dimensions), stride * blocksize, 0);
            // auto inter_begin = inter_block_range->begin();
            // auto inter_end = inter_block_range->end();
            // for (auto block = inter_begin; block != inter_end; ++block) {
            //     auto end_idx = block.get_global_index();
            //     for (int i = 0; i < N; i++) {
            //         end_idx[i] += stride * blocksize;
            //         if (end_idx[i] > global_dimensions[i] - 1) {
            //             end_idx[i] = global_dimensions[i] - 1;
            //         }
            //     }
            //     block_interpolation(dec_data, block.get_global_index(), end_idx, PB_recover,
            //                         interpolators[interpolator_id], direction_sequence_id, stride);
            // }
        // }
        // for (uint level = interpolation_level; level > 0 && level <= interpolation_level; level--) {
        //     if (level >= 3) {
        //         quantizer.set_eb(eb * eb_ratio);
        //     } else {
        //         quantizer.set_eb(eb);
        //     }
        //     size_t stride = 1U << (level - 1);
        //     auto inter_block_range = std::make_shared<multi_dimensional_range<T, N>>(
        //         dec_data, std::begin(global_dimensions), std::end(global_dimensions), stride * blocksize, 0);
        //     auto inter_begin = inter_block_range->begin();
        //     auto inter_end = inter_block_range->end();
        //     for (auto block = inter_begin; block != inter_end; ++block) {
        //         auto end_idx = block.get_global_index();
        //         for (int i = 0; i < N; i++) {
        //             end_idx[i] += stride * blocksize;
        //             if (end_idx[i] > global_dimensions[i] - 1) {
        //                 end_idx[i] = global_dimensions[i] - 1;
        //             }
        //         }
        //         block_interpolation(dec_data, block.get_global_index(), end_idx, PB_recover,
        //                             interpolators[interpolator_id], direction_sequence_id, stride);
        //     }
        // }
        quantizer.postdecompress_data();
        //            timer.stop("Interpolation Decompress");

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
        std::copy_n(conf.dims.begin(), N, global_dimensions.begin());
        blocksize = 32;
        // blocksize = 65536;
        interpolator_id = conf.interpAlgo;
        direction_sequence_id = conf.interpDirection;

        init();

        std::vector<int> quant_inds_vec(num_elements);
        quant_inds = quant_inds_vec.data();

        double eb = quantizer.get_eb();

        //            quant_inds.push_back(quantizer.quantize_and_overwrite(*data, 0));
        quant_inds[quant_index++] = quantizer.quantize_and_overwrite(*data, 0);

        //            Timer timer;
        //            timer.start();
        // int temp = interpolation_level;
        interpolation_level = level_dimensions.size();
        std::array<int, 4> last_dim = {1, 1, 1, 1};
        int last_dir = 0;

        for (uint level = interpolation_level - 1; level >= 0 && level < interpolation_level; level--) {
            if (level >= 3) {
                quantizer.set_eb(eb * eb_ratio);
            } else {
                quantizer.set_eb(eb);
            }
            { // Log
                std::cout << level << std::endl;
            }
            // size_t stride = 1U << (level - 1);
            // std::cout << "hh\n";

            std::array<int, 3> strides = calc_stride(level_dimensions[level]);
            int dir = 0;
            int dir2 = 0;
            bool foundone = false;
            bool foundtwo = false;
            { // predict behavier
                
                for(int i = 0; i < 3; i++) {
                    if(level_dimensions[level][i] > last_dim[i]){
                        
                        if(foundone) {
                            dir2 = i;
                            foundtwo = true;
                        } else {
                            dir = i;
                        }
                        foundone = true;
                    }
                }
                // int last_digit = (level_dimensions[level][3] % 10);
                // switch (last_digit)
                // {
                // case 1:
                //     dir = 2;
                //     break;
                // case 2:
                //     dir = 1;
                //     break;
                // case 3:
                //     dir = 0;
                //     break;
                // default:
                //     break;
                // }
                last_dim = level_dimensions[level];
            }
            std::vector<std::array<int, 3>> begins, ends;
            std::cout << level_dimensions[level][0] << ' ' << level_dimensions[level][1] << ' ' << level_dimensions[level][2] << std::endl;
            block_divider(level_dimensions[level], begins, ends);
            // std::cout << begins.size() << ' ' << ends.size() << std::endl;
            if(foundtwo) dir = 3 - dir - dir2;
            for(int i = 0; i < begins.size(); i++) {
                // std::cout << "block" << i << ": " << begins[i][0] << ' ' << begins[i][1] << ' ' << begins[i][2] << " to " << ends[i][0] << ' ' << ends[i][1] << ' ' << ends[i][2] << std::endl;
                if(foundtwo) {
                    printf("f11\n");
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 221, strides, dir);
                } else if (foundone) {
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 411, strides, dir);
                } else {
                    interpolation(data, begins[i], ends[i], PB_predict_overwrite, interpolators[interpolator_id], 111, strides, last_dir);
                }
                // { // Log
                //     std::cout << "quant_index: " << quant_index << std::endl;
                // }
            }
            last_dir = dir;


            // auto inter_block_range = std::make_shared<multi_dimensional_range<T, N>>(
            //     data, std::begin(global_dimensions), std::end(global_dimensions), blocksize * stride, 0);

            // auto inter_begin = inter_block_range->begin();
            // auto inter_end = inter_block_range->end();

            // for (auto block = inter_begin; block != inter_end; ++block) {
            //     auto end_idx = block.get_global_index();
            //     for (int i = 0; i < N; i++) {
            //         end_idx[i] += blocksize * stride;
            //         if (end_idx[i] > global_dimensions[i] - 1) {
            //             end_idx[i] = global_dimensions[i] - 1;
            //         }
            //     }

            //     block_interpolation(data, block.get_global_index(), end_idx, PB_predict_overwrite,
            //                         interpolators[interpolator_id], direction_sequence_id, stride);
            //     { // Log
            //         std::cout << "quant_index: " << quant_index << std::endl;
            //     }
            // }
        }
        // interpolation_level = temp;
        // for (uint level = interpolation_level; level > 0 && level <= interpolation_level; level--) {
        //     if (level >= 3) {
        //         quantizer.set_eb(eb * eb_ratio);
        //     } else {
        //         quantizer.set_eb(eb);
        //     }
        //     { // Log
        //         std::cout << level << std::endl;
        //     }
        //     size_t stride = 1U << (level - 1);

        //     auto inter_block_range = std::make_shared<multi_dimensional_range<T, N>>(
        //         data, std::begin(global_dimensions), std::end(global_dimensions), blocksize * stride, 0);

        //     auto inter_begin = inter_block_range->begin();
        //     auto inter_end = inter_block_range->end();

        //     for (auto block = inter_begin; block != inter_end; ++block) {
        //         auto end_idx = block.get_global_index();
        //         for (int i = 0; i < N; i++) {
        //             end_idx[i] += blocksize * stride;
        //             if (end_idx[i] > global_dimensions[i] - 1) {
        //                 end_idx[i] = global_dimensions[i] - 1;
        //             }
        //         }

        //         block_interpolation(data, block.get_global_index(), end_idx, PB_predict_overwrite,
        //                             interpolators[interpolator_id], direction_sequence_id, stride);
        //         { // Log
        //             std::cout << "quant_index: " << quant_index << std::endl;
        //         }
        //     }
        // }

        quantizer.postcompress_data();
        return quant_inds_vec;
    }

    void save(uchar *&c) override {
        write(global_dimensions.data(), N, c);
        write(blocksize, c);
        write(interpolator_id, c);
        write(direction_sequence_id, c);

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

        size_t coeff_size = 0;
        read(coeff_size, c, remaining_length);
        coeff_list.resize(coeff_size);
        for(int i = 0; i < coeff_size; i++) {
            size_t J = 0;
            read(J, c, remaining_length);
            coeff_list[i].resize(J);
            read(coeff_list[i].data(), J, c, remaining_length);
            // std::cout << J << std::endl;
        }
        quantizer.load(c, remaining_length);
    }

    std::pair<int, int> get_out_range() override { return quantizer.get_out_range(); }

   private:
    enum PredictorBehavior { PB_predict_overwrite, PB_predict, PB_recover };

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
        std::ifstream infile("Uf48.bin.dat2.txt"); 
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

        for (auto arr : level_dimensions) {
            for (int val : arr) {
                std::cout << val << " ";
            }
            std::cout << '\n';
            std::array<int, 3> strides = calc_stride(arr);
            std::cout << "stride: ";
            for (int val : strides) {
                std::cout << val << " ";
            }
            std::cout <<"\n\n";
        }
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

        level_dimension_loader();
    }

    inline void quantize(size_t idx, T &d, T pred) {
        {   // debug
            if(quant_index < 100) {
                std::cout << "(x, y, z) = (" << idx/(96*96) << ", " << (idx % (96*96))/96 << ", " << (idx % 96) << ")" << std::endl;
            }
        }
        
        quant_inds[quant_index++] = (quantizer.quantize_and_overwrite(d, pred));
    }

    inline void recover(size_t idx, T &d, T pred) { d = quantizer.recover(pred, quant_inds[quant_index++]); }
    
    void calc_coeff(T *data, size_t begin, size_t end, size_t stride) {
        size_t n = (end - begin) / stride + 1;
        if (n <= 1) {
            return;
        }
        // 用来累加 A^T A 和 A^T b 所需要的元素
        long double sumA00 = 0.0;  // = \sum (a_i^{(0)})^2
        long double sumA01 = 0.0;  // = \sum (a_i^{(0)} a_i^{(1)})
        long double sumA11 = 0.0;  // = \sum (a_i^{(1)})^2
        long double sumAB0 = 0.0;  // = \sum (a_i^{(0)} b_i)
        long double sumAB1 = 0.0;  // = \sum (a_i^{(1)} b_i)
        long double lambda = 0.0001;
        for (size_t i = 0; i + 2 < n; i += 2) {
            T a0 = *(data + begin + i * stride);
            T bVal = *(data + begin + (i + 1) * stride);
            T a1 = *(data + begin + (i + 2) * stride);
            sumA00 += a0 * a0;
            sumA01 += a0 * a1;
            sumA11 += a1 * a1;
            sumAB0 += a0 * bVal;
            sumAB1 += a1 * bVal;
        }
        // 构造正则化后的 ATA_reg = (A^T A + lambda I)
        // 其中 A^T A = [ sumA00   sumA01 ]
        //              [ sumA01   sumA11 ]
        // 加上 lambda I = [ lambda  0 ]
        //                 [ 0       lambda ]
        // 得到:
        // ATA_reg = [ sumA00+lambda   sumA01      ]
        //           [ sumA01          sumA11+lambda]
        long double a = sumA00 + lambda;
        long double b = sumA01;
        long double d = sumA11 + lambda;

        // 构造向量 ATb = [ sumAB0 ]
        //                [ sumAB1 ]
        long double v0 = sumAB0;
        long double v1 = sumAB1;

        // 求行列式
        long double det = a * d - b * b;
        if (std::fabs(det) < 1e-20L) {
            std::cerr << "Error: matrix is singular or nearly singular." << std::endl;
            return;
        }

        // 2x2 矩阵的逆
        // [ a  b ]^-1 = (1/det) [  d  -b ]
        // [ b  d ]              [ -b  a  ]
        long double invA =  d / det;    // d/det
        long double invB = -b / det;    // -b/det
        long double invD =  a / det;    // a/det

        // x = (ATA_reg)^{-1} * (ATb)
        long double x0 = invA * v0 + invB * v1;
        long double x1 = invB * v0 + invD * v1;

        coeff_list.push_back(std::vector<_Float32>{static_cast<_Float32>(x0), static_cast<_Float32>(x1)});
    }


    double block_interpolation_3d(T *data, size_t begin, size_t end, size_t stride, size_t stride_p1, size_t stride_p2, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (end - begin) / stride + 1;
        if (n <= 1) {
            return 0;
        }
        double predict_error = 0;

        if (pb == PB_predict_overwrite) {
            for (size_t i = 1; i + 1 < n; i += 2) {
                T *d = data + begin + i * stride;
                quantize(d - data, *d, interp_linear_3d(*(d - stride), 
                                                        *(d - stride - stride_p1 - stride_p2),
                                                        *(d - stride - stride_p2),
                                                        *(d - stride + stride_p1 - stride_p2),
                                                        *(d - stride - stride_p1),
                                                        *(d - stride + stride_p1),
                                                        *(d - stride - stride_p1 + stride_p2),
                                                        *(d - stride + stride_p2),
                                                        *(d - stride + stride_p1 + stride_p2),
                                                        *(d + stride), 
                                                        *(d + stride - stride_p1 - stride_p2),
                                                        *(d + stride - stride_p2),
                                                        *(d + stride + stride_p1 - stride_p2),
                                                        *(d + stride - stride_p1),
                                                        *(d + stride + stride_p1),
                                                        *(d + stride - stride_p1 + stride_p2),
                                                        *(d + stride + stride_p2),
                                                        *(d + stride + stride_p1 + stride_p2)));
            }
            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                if (n < 4) {
                    quantize(d - data, *d, *(d - stride));
                } else {
                    quantize(d - data, *d, interp_linear1_3d(*(d - stride), 
                                                        *(d - stride - stride_p1 - stride_p2),
                                                        *(d - stride - stride_p2),
                                                        *(d - stride + stride_p1 - stride_p2),
                                                        *(d - stride - stride_p1),
                                                        *(d - stride + stride_p1),
                                                        *(d - stride - stride_p1 + stride_p2),
                                                        *(d - stride + stride_p2),
                                                        *(d - stride + stride_p1 + stride_p2)
                                                        ));
                }
            }
        } else {
            for (size_t i = 1; i + 1 < n; i += 2) {
                T *d = data + begin + i * stride;
                recover(d - data, *d, interp_linear_3d(*(d - stride), 
                                                        *(d - stride - stride_p1 - stride_p2),
                                                        *(d - stride - stride_p2),
                                                        *(d - stride + stride_p1 - stride_p2),
                                                        *(d - stride - stride_p1),
                                                        *(d - stride + stride_p1),
                                                        *(d - stride - stride_p1 + stride_p2),
                                                        *(d - stride + stride_p2),
                                                        *(d - stride + stride_p1 + stride_p2),
                                                        *(d + stride), 
                                                        *(d + stride - stride_p1 - stride_p2),
                                                        *(d + stride - stride_p2),
                                                        *(d + stride + stride_p1 - stride_p2),
                                                        *(d + stride - stride_p1),
                                                        *(d + stride + stride_p1),
                                                        *(d + stride - stride_p1 + stride_p2),
                                                        *(d + stride + stride_p2),
                                                        *(d + stride + stride_p1 + stride_p2)));
            }
            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                if (n < 4) {
                    recover(d - data, *d, *(d - stride));
                } else {
                    recover(d - data, *d, interp_linear1_3d(*(d - stride), 
                                                        *(d - stride - stride_p1 - stride_p2),
                                                        *(d - stride - stride_p2),
                                                        *(d - stride + stride_p1 - stride_p2),
                                                        *(d - stride - stride_p1),
                                                        *(d - stride + stride_p1),
                                                        *(d - stride - stride_p1 + stride_p2),
                                                        *(d - stride + stride_p2),
                                                        *(d - stride + stride_p1 + stride_p2)
                                                        ));
                }
            }
        }
        return predict_error;
    }
    double block_interpolation_2d(T *data, size_t begin, size_t end, size_t stride, size_t stride_pendicular, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin: " << begin << ", end: " << end << ", stride: " << stride << std::endl;
        // }
        size_t n = (end - begin) / stride + 1;
        if (n <= 1) {
            return 0;
        }
        double predict_error = 0;

        // 
        if (pb == PB_predict_overwrite) {
            for (size_t i = 1; i + 1 < n; i += 2) {
                T *d = data + begin + i * stride;
                quantize(d - data, *d, interp_linear_2d(*(d - stride), 
                                                        *(d - stride - stride_pendicular),
                                                        *(d - stride + stride_pendicular),
                                                        *(d + stride),
                                                        *(d + stride - stride_pendicular),
                                                        *(d + stride + stride_pendicular)
                                                        ));
            }
            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                if (n < 4) {
                    quantize(d - data, *d, *(d - stride));
                } else {
                    quantize(d - data, *d, interp_linear1_2d(*(d - stride), 
                                                        *(d - stride - stride_pendicular),
                                                        *(d - stride + stride_pendicular)));
                }
            }
        } else {
            for (size_t i = 1; i + 1 < n; i += 2) {
                T *d = data + begin + i * stride;
                recover(d - data, *d, interp_linear_2d(*(d - stride), 
                                                        *(d - stride - stride_pendicular),
                                                        *(d - stride + stride_pendicular),
                                                        *(d + stride),
                                                        *(d + stride - stride_pendicular),
                                                        *(d + stride + stride_pendicular)
                                                        ));
            }
            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                if (n < 4) {
                    recover(d - data, *d, *(d - stride));
                } else {
                    recover(d - data, *d, interp_linear1_2d(*(d - stride), 
                                                        *(d - stride - stride_pendicular),
                                                        *(d - stride + stride_pendicular)));
                }
            }
        }
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
                quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), .5, .5));
            }
                // std::cout << "a3" << std::endl;

            if (n % 2 == 0) {
                T *d = data + begin + (n - 1) * stride;
                // std::cout << "a4" << std::endl;

                if (n < 4) {
                    // std::cout << "n=2\n" << std::endl;
                    quantize(d - data, *d, *(d - stride));
                } else {
                    quantize(d - data, *d, interp_linear1(*(d - stride * 3), *(d - stride)));
                }
            }
        } else {
            float x0 = 0.5;
            float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            coeff_idx++;
            for (size_t i = 1; i + 1 < n; i += 2) {
                T *d = data + begin + i * stride;
                // recover(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear(*(d - stride), *(d + stride), .5, .5));
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
        

        return predict_error;
    }
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
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            coeff_idx++;
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
            coeff_idx++;
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
            coeff_idx++;
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
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                quantize(d - data, *d, interp_linear_2d_22x(*(d - stride_p1), *(d + stride_p1), *(d - stride_p2), *(d + stride_p2)));
            }
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            coeff_idx++;
            if (startfrombot) {
                T *d = data + begin;
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1), *(d + stride_p1), *(d - stride_p2), *(d + stride_p2)));
            } 
            for (size_t i = 1; i < n; i++) {
                T *d = data + begin + i * stride;
                // quantize(d - data, *d, interp_linear(*(d - stride), *(d + stride), x0, x1));
                recover(d - data, *d, interp_linear_2d_22x(*(d - stride_p1), *(d + stride_p1), *(d - stride_p2), *(d + stride_p2)));
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
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            coeff_idx++;
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
        } else {
            // float x0 = 0.5;
            // float x1 = 0.5;
            // if(coeff_idx < coeff_list.size()) {
            //     x0 = coeff_list[coeff_idx][0];
            //     x1 = coeff_list[coeff_idx][1];
            // }
            coeff_idx++;
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
        return predict_error;
    }
    double interpolation_22x(T *data, std::array<int, 3> begin_real, std::array<int, 3> end_real, std::array<int, 3> strides, int dir, const std::string &interp_func,
                                  const PredictorBehavior pb) {
        // { // Log
        //     std::cout << "[Log] begin_real: " << begin_real << ", end_real: " << end << ", stride: " << stride << std::endl;
        // }
        std::cout << "dir=" << dir << std::endl;

        std::array<int, 3> order{0, 0, 0};
        {
            switch (dir)
            {
            case 0:
                order = {1, 2, 0};
                std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }
        double predict_error = 0;
        std::cout << "f33" << std::endl;
        for (size_t i = begin_real[order[0]] + strides[order[0]]; i <= end_real[order[0]]; i += 2 * strides[order[0]]) {
            for (size_t j = begin_real[order[1]] + strides[order[1]]; j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];
                if(i == end_real[order[0]]) {
                    if(j == end_real[order[1]]) {
                        std::cout << "corner2" << std::endl;
                        predict_error += block_interpolation_2d_22_corner2(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    } else {
                        std::cout << "corner11" << std::endl;

                        predict_error += block_interpolation_2d_22_corner1(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    }
                } else if(j == end_real[order[1]]) {
                        std::cout << "corner12" << std::endl;
                    predict_error += block_interpolation_2d_22_corner1(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb, !bool(begin_real[order[2]]));
                } else {
                    std::cout << "mid" << std::endl;
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
                std::cout << "order1,2,0" << std::endl;
                break;
            case 1:
                order = {0, 2, 1};
                std::cout << "order0,2,1" << std::endl;
                break;
            case 2:
                order = {0, 1, 2};
                std::cout << "order0,1,2" << std::endl;
                break;
            
            default:
                break;
            }
        }
        double predict_error = 0;
        int cnt_i = 0;
        if(begin_real[order[0]]) cnt_i++;
        for (size_t i = (begin_real[order[0]] ? begin_real[order[0]] + strides[order[0]] : 0); i <= end_real[order[0]]; i += strides[order[0]], cnt_i++) {
            bool even_i = (cnt_i % 2 == 0);
            for (size_t j = ((even_i)? begin_real[order[1]] + strides[order[1]] : (begin_real[order[1]] ? begin_real[order[1]] + 2 * strides[order[1]] : 0)); j <= end_real[order[1]]; j += 2 * strides[order[1]]) {
                size_t begin_real_offset = i * dimension_offsets[order[0]] + j * dimension_offsets[order[1]] +
                                      begin_real[order[2]] * dimension_offsets[order[2]];

                if(i == begin_real[order[0]]) {
                    if(begin_real[order[0]]) {continue; }
                    else {
                        if(j == end_real[order[1]]) {
                            // top left corner
                            std::cout << "top left corner" << std::endl;
                            
                            predict_error += block_interpolation_2d_23_corner(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], -strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                        } else {
                            // left edge
                            std::cout << "left edge" << std::endl;

                            predict_error += block_interpolation_2d_23_edge(
                                data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                                strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));

                        }
                    }
                } else if(i == end_real[order[0]]) {
                    if(j == 0) {
                        // bot right corner
                        std::cout << "bot right corner" << std::endl;
                        
                        predict_error += block_interpolation_2d_23_corner(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], -strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    } else if(j == end_real[order[1]]) {
                        // top right corner
                        std::cout << "top right corner" << std::endl;
                        std::cout << "stride = " << strides[order[1]] << " begin = " << begin_real[order[1]] << " end=" <<end_real[order[1]] << " cnt_i = " << cnt_i << " even_i" << even_i << std::endl;
                        std::cout << "begin x = " << begin_real[order[0]] << " j=" << j << std::endl;
                        predict_error += block_interpolation_2d_23_corner(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    } else {
                        // right edge
                        std::cout << "right edge" << std::endl;

                        predict_error += block_interpolation_2d_23_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[1]] * dimension_offsets[order[1]], interp_func, pb, !bool(begin_real[order[2]]));
                    }
                } else if(j == 0) {
                    // bot edge
                    std::cout << "bot edge" << std::endl;
                    
                    predict_error += block_interpolation_2d_23_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb, !bool(begin_real[order[2]]));
                } else if(j == end_real[order[1]]) {
                    // top edge
                    std::cout << "top edge" << std::endl;
                    std::cout << "stride = " << strides[order[1]] << " begin = " << begin_real[order[1]] << " end=" <<end_real[order[1]] << " cnt_i = " << cnt_i << " even_i" << even_i << std::endl;
                    std::cout << "begin x = " << begin_real[order[0]] << " j=" << j << std::endl;
                    predict_error += block_interpolation_2d_23_edge(
                            data, begin_real_offset, begin_real_offset + (end_real[order[2]] - begin_real[order[2]]) * dimension_offsets[order[2]],
                            strides[order[2]] * dimension_offsets[order[2]], strides[order[0]] * dimension_offsets[order[0]], interp_func, pb, !bool(begin_real[order[2]]));
                } else {
                    std::cout << "mid" << std::endl;
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

        if(action > 400) {
            // std::cout << "f41\n" << std::endl;

            return interpolation_41x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else if(action > 200) {
            return interpolation_22x(data, begin_real, end_real, strides,dir, interp_func, pb);
        } else {
            // std::cout << "f22\n" << std::endl;
            return interpolation_23x(data, begin_real, end_real, strides,dir, interp_func, pb);
        }
    }

    template <uint NN = N>
    typename std::enable_if<NN == 1, double>::type block_interpolation(T *data, std::array<size_t, N> begin,
                                                                       std::array<size_t, N> end,
                                                                       const PredictorBehavior pb,
                                                                       const std::string &interp_func,
                                                                       const int direction, size_t stride = 1) {
        return block_interpolation_1d(data, begin[0], end[0], stride, interp_func, pb);
    }

    template <uint NN = N>
    typename std::enable_if<NN == 2, double>::type block_interpolation(T *data, std::array<size_t, N> begin,
                                                                       std::array<size_t, N> end,
                                                                       const PredictorBehavior pb,
                                                                       const std::string &interp_func,
                                                                       const int direction, size_t stride = 1) {
        double predict_error = 0;
        size_t stride2x = stride * 2;
        const std::array<int, N> dims = dimension_sequences[direction];
        for (size_t j = (begin[dims[1]] ? begin[dims[1]] + stride2x : 0); j <= end[dims[1]]; j += stride2x) {
            size_t begin_offset = begin[dims[0]] * dimension_offsets[dims[0]] + j * dimension_offsets[dims[1]];
            predict_error += block_interpolation_1d(
                data, begin_offset, begin_offset + (end[dims[0]] - begin[dims[0]]) * dimension_offsets[dims[0]],
                stride * dimension_offsets[dims[0]], interp_func, pb);
        }
        for (size_t i = (begin[dims[0]] ? begin[dims[0]] + stride : 0); i <= end[dims[0]]; i += stride) {
            size_t begin_offset = i * dimension_offsets[dims[0]] + begin[dims[1]] * dimension_offsets[dims[1]];
            predict_error += block_interpolation_1d(
                data, begin_offset, begin_offset + (end[dims[1]] - begin[dims[1]]) * dimension_offsets[dims[1]],
                stride * dimension_offsets[dims[1]], interp_func, pb);
        }
        return predict_error;
    }

    template <uint NN = N>
    typename std::enable_if<NN == 3, double>::type block_interpolation(T *data, std::array<size_t, N> begin,
                                                                       std::array<size_t, N> end,
                                                                       const PredictorBehavior pb,
                                                                       const std::string &interp_func,
                                                                       const int direction, size_t stride = 1) {
        double predict_error = 0;
        size_t stride2x = stride * 2;
        const std::array<int, N> dims = dimension_sequences[direction];
        {   // print dims, begin, end
            std::cout << "dimension_offsets = {";
            for (size_t i = 0; i < dimension_offsets.size(); ++i) {
                std::cout << dimension_offsets[i];
                if (i < dimension_offsets.size() - 1) {
                    std::cout << ", ";
                }
            }
            std::cout << "}" << std::endl;

            std::cout << "begin = {";
            for (size_t i = 0; i < begin.size(); ++i) {
                std::cout << begin[i];
                if (i < begin.size() - 1) {
                    std::cout << ", ";
                }
            }
            std::cout << "}" << std::endl;
            
            std::cout << "end = {";
            for (size_t i = 0; i < end.size(); ++i) {
                std::cout << end[i];
                if (i < end.size() - 1) {
                    std::cout << ", ";
                }
            }
            std::cout << "}" << std::endl;

            std::cout << "stride = " << stride << std::endl;

        }
        for (size_t j = (begin[dims[1]] ? begin[dims[1]] + stride2x : 0); j <= end[dims[1]]; j += stride2x) {
            for (size_t k = (begin[dims[2]] ? begin[dims[2]] + stride2x : 0); k <= end[dims[2]]; k += stride2x) {
                size_t begin_offset = begin[dims[0]] * dimension_offsets[dims[0]] + j * dimension_offsets[dims[1]] +
                                      k * dimension_offsets[dims[2]];
                predict_error += block_interpolation_1d(
                    data, begin_offset, begin_offset + (end[dims[0]] - begin[dims[0]]) * dimension_offsets[dims[0]],
                    stride * dimension_offsets[dims[0]], interp_func, pb);
            }
        }
        for (size_t i = (begin[dims[0]] ? begin[dims[0]] + stride : 0); i <= end[dims[0]]; i += stride) {
            for (size_t k = (begin[dims[2]] ? begin[dims[2]] + stride2x : 0); k <= end[dims[2]]; k += stride2x) {
                size_t begin_offset = i * dimension_offsets[dims[0]] + begin[dims[1]] * dimension_offsets[dims[1]] +
                                      k * dimension_offsets[dims[2]];
                if(i == ((begin[dims[0]] ? begin[dims[0]] + stride : 0)) ||
                    i + stride > end[dims[0]] ||
                    k == ((begin[dims[2]] ? begin[dims[2]] + stride2x : 0)) ||
                    k + stride2x > end[dims[2]]) {
                    predict_error += block_interpolation_1d(
                        data, begin_offset, begin_offset + (end[dims[1]] - begin[dims[1]]) * dimension_offsets[dims[1]],
                        stride * dimension_offsets[dims[1]], interp_func, pb);
                } else {
                    predict_error += block_interpolation_2d(
                        data, begin_offset, begin_offset + (end[dims[1]] - begin[dims[1]]) * dimension_offsets[dims[1]],
                        stride * dimension_offsets[dims[1]], stride * dimension_offsets[dims[0]], interp_func, pb);
                    // predict_error += block_interpolation_1d(
                    //     data, begin_offset, begin_offset + (end[dims[1]] - begin[dims[1]]) * dimension_offsets[dims[1]],
                    //     stride * dimension_offsets[dims[1]], interp_func, pb);
                }

            }
        }
        for (size_t i = (begin[dims[0]] ? begin[dims[0]] + stride : 0); i <= end[dims[0]]; i += stride) {
            for (size_t j = (begin[dims[1]] ? begin[dims[1]] + stride : 0); j <= end[dims[1]]; j += stride) {
                size_t begin_offset = i * dimension_offsets[dims[0]] + j * dimension_offsets[dims[1]] +
                                      begin[dims[2]] * dimension_offsets[dims[2]];
                if(i == ((begin[dims[0]] ? begin[dims[0]] + stride : 0)) ||
                    i + stride > end[dims[0]]) {
                    if(j == ((begin[dims[1]] ? begin[dims[1]] + stride : 0)) ||
                        j + stride > end[dims[1]]
                    ) {
                        predict_error += block_interpolation_1d(
                            data, begin_offset, begin_offset + (end[dims[2]] - begin[dims[2]]) * dimension_offsets[dims[2]],
                            stride * dimension_offsets[dims[2]], interp_func, pb);
                    } else {
                        predict_error += block_interpolation_2d(
                            data, begin_offset, begin_offset + (end[dims[2]] - begin[dims[2]]) * dimension_offsets[dims[2]],
                            stride * dimension_offsets[dims[2]], stride * dimension_offsets[dims[1]], interp_func, pb);
                    }
                } else if (j == ((begin[dims[1]] ? begin[dims[1]] + stride : 0)) ||
                        j + stride > end[dims[1]]) {
                    predict_error += block_interpolation_2d(
                            data, begin_offset, begin_offset + (end[dims[2]] - begin[dims[2]]) * dimension_offsets[dims[2]],
                            stride * dimension_offsets[dims[2]], stride * dimension_offsets[dims[0]], interp_func, pb);
                } else {
                    predict_error += block_interpolation_3d(
                        data, begin_offset, begin_offset + (end[dims[2]] - begin[dims[2]]) * dimension_offsets[dims[2]],
                        stride * dimension_offsets[dims[2]], stride * dimension_offsets[dims[0]], stride * dimension_offsets[dims[1]], interp_func, pb);
                }
                // predict_error += block_interpolation_1d(
                //             data, begin_offset, begin_offset + (end[dims[2]] - begin[dims[2]]) * dimension_offsets[dims[2]],
                //             stride * dimension_offsets[dims[2]], interp_func, pb);
            }
        }
        return predict_error;
    }

    template <uint NN = N>
    typename std::enable_if<NN == 4, double>::type block_interpolation(T *data, std::array<size_t, N> begin,
                                                                       std::array<size_t, N> end,
                                                                       const PredictorBehavior pb,
                                                                       const std::string &interp_func,
                                                                       const int direction, size_t stride = 1) {
        double predict_error = 0;
        size_t stride2x = stride * 2;
        max_error = 0;
        const std::array<int, N> dims = dimension_sequences[direction];
        for (size_t j = (begin[dims[1]] ? begin[dims[1]] + stride2x : 0); j <= end[dims[1]]; j += stride2x) {
            for (size_t k = (begin[dims[2]] ? begin[dims[2]] + stride2x : 0); k <= end[dims[2]]; k += stride2x) {
                for (size_t t = (begin[dims[3]] ? begin[dims[3]] + stride2x : 0); t <= end[dims[3]]; t += stride2x) {
                    size_t begin_offset = begin[dims[0]] * dimension_offsets[dims[0]] + j * dimension_offsets[dims[1]] +
                                          k * dimension_offsets[dims[2]] + t * dimension_offsets[dims[3]];
                    predict_error += block_interpolation_1d(
                        data, begin_offset, begin_offset + (end[dims[0]] - begin[dims[0]]) * dimension_offsets[dims[0]],
                        stride * dimension_offsets[dims[0]], interp_func, pb);
                }
            }
        }
        max_error = 0;
        for (size_t i = (begin[dims[0]] ? begin[dims[0]] + stride : 0); i <= end[dims[0]]; i += stride) {
            for (size_t k = (begin[dims[2]] ? begin[dims[2]] + stride2x : 0); k <= end[dims[2]]; k += stride2x) {
                for (size_t t = (begin[dims[3]] ? begin[dims[3]] + stride2x : 0); t <= end[dims[3]]; t += stride2x) {
                    size_t begin_offset = i * dimension_offsets[dims[0]] + begin[dims[1]] * dimension_offsets[dims[1]] +
                                          k * dimension_offsets[dims[2]] + t * dimension_offsets[dims[3]];
                    predict_error += block_interpolation_1d(
                        data, begin_offset, begin_offset + (end[dims[1]] - begin[dims[1]]) * dimension_offsets[dims[1]],
                        stride * dimension_offsets[dims[1]], interp_func, pb);
                }
            }
        }
        max_error = 0;
        for (size_t i = (begin[dims[0]] ? begin[dims[0]] + stride : 0); i <= end[dims[0]]; i += stride) {
            for (size_t j = (begin[dims[1]] ? begin[dims[1]] + stride : 0); j <= end[dims[1]]; j += stride) {
                for (size_t t = (begin[dims[3]] ? begin[dims[3]] + stride2x : 0); t <= end[dims[3]]; t += stride2x) {
                    size_t begin_offset = i * dimension_offsets[dims[0]] + j * dimension_offsets[dims[1]] +
                                          begin[dims[2]] * dimension_offsets[dims[2]] + t * dimension_offsets[dims[3]];
                    predict_error += block_interpolation_1d(
                        data, begin_offset, begin_offset + (end[dims[2]] - begin[dims[2]]) * dimension_offsets[dims[2]],
                        stride * dimension_offsets[dims[2]], interp_func, pb);
                }
            }
        }

        max_error = 0;
        for (size_t i = (begin[dims[0]] ? begin[dims[0]] + stride : 0); i <= end[dims[0]]; i += stride) {
            for (size_t j = (begin[dims[1]] ? begin[dims[1]] + stride : 0); j <= end[dims[1]]; j += stride) {
                for (size_t k = (begin[dims[2]] ? begin[dims[2]] + stride : 0); k <= end[dims[2]]; k += stride) {
                    size_t begin_offset = i * dimension_offsets[dims[0]] + j * dimension_offsets[dims[1]] +
                                          k * dimension_offsets[dims[2]] + begin[dims[3]] * dimension_offsets[dims[3]];
                    predict_error += block_interpolation_1d(
                        data, begin_offset, begin_offset + (end[dims[3]] - begin[dims[3]]) * dimension_offsets[dims[3]],
                        stride * dimension_offsets[dims[3]], interp_func, pb);
                }
            }
        }
        return predict_error;
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

    // coeff
    std::vector<std::vector<_Float32>> coeff_list;
    size_t coeff_idx = 0;
    std::vector<std::array<int, 4>> level_dimensions;

};

template <class T, uint N, class Quantizer>
FHDEDecomposition<T, N, Quantizer> make_decomposition_FHDE(const Config &conf, Quantizer quantizer) {
    return FHDEDecomposition<T, N, Quantizer>(conf, quantizer);
}

}  // namespace SZ3

#endif
