#include <cstddef>
#include <cstdio>
#include <cstdlib>

inline void usage()
{
    printf("Usage: fhde <options>\n");
    printf("Options:\n");
    printf("* general options:\n");
    printf("    -h: print the help information\n");
    printf("    -a: print compression results such as distortions\n");
    printf("* input and output:\n");
    printf("    -i <path>: original input file in binary format\n");
    printf("    -o <path>: decompressed file in binary format\n");
    printf("    -z <path>: compressed file\n");
    printf("* data type:\n");
    printf("    -f: single precision (float type)\n");
    printf("* configuration file:\n");
    printf("    -c <configuration file>: configuration file\n");
    printf("* error control:\n");
    printf("    -E <error control mode> <error bound (optional)>\n");
    printf("    error control mode as follows:\n");
    printf("        REL (value range based error bound, so a.k.a., VR_REL)\n");
    printf("    error bound can be set directly after the error control mode, or separately with the following options:\n");
    printf("        -R <value_range based relative error bound>: specifying relative error bound\n");
    printf("* dimensions:\n");
    printf("    -3 <nx> <ny> <nz>: dimensions for 3D data such as data[nz][ny][nx]\n");
    exit(0);
}

int main(int argc,char **argv)
{
    bool compression=false;
    bool decompression=false;
    char *inPath=nullptr;
    char *cmpPath=nullptr;
    char *conPath=nullptr;
    char *decPath=nullptr;
    bool delCmpPath=false;

    char *errBoundMode=nullptr;
    char *errBound=nullptr;
    char *relErrorBound=nullptr;

    size_t r4=0;
    size_t r3=0;
    size_t r2=0;
    size_t r1=0;

    size_t i=0;
    if (argc==1)
        usage();
    int width=-1;
    exit(0);
    // for (i=1;i<argc;i++)
    // {
    //     if (argv[i][0] != '-' || argv[i][2]) {
    //         if (argv[i][1]=='h' && argv[i][2]=='2') {
    //             usage_sz2();
    //         } else {
    //             usage();
    //         }
    //     }
    //     switch (argv[i][1]) {
    //         case 'h':
    //             usage();
    //             exit(0);
    //         case 'v':
    //             printf("version: %s\n", SZ3_VER);
    //             exit(0);
    //         case 'b':
    //             binaryOutput=true;
    //             break;
    //         case 't':
    //             binaryOutput=false;
    //             break;
    //         case 'a':
    //             printCmpResults=1;
    //             break;
    //         case 'z':
    //             compression=true;
    //             if (i + 1 < argc) {
    //                 cmpPath=argv[i + 1];
    //                 if (cmpPath[0] != '-')
    //                     i++;
    //                 else
    //                     cmpPath=nullptr;
    //             }
    //             break;
    //         case 'x':
    //             sz2mode=true;
    //             decompression=true;
    //             if (i + 1 < argc) {
    //                 decPath=argv[i + 1];
    //                 if (decPath[0] != '-')
    //                     i++;
    //                 else
    //                     decPath=nullptr;
    //             }
    //             break;
    //         case 'f':
    //             dataType=SZ_FLOAT;
    //             break;
    //         case 'd':
    //             dataType=SZ_DOUBLE;
    //             break;
    //         case 'I':
    //             if (++i==argc || sscanf(argv[i], "%d", &width) != 1) {
    //                 usage();
    //             }
    //             if (width==32) {
    //                 dataType=SZ_INT32;
    //             } else if (width==64) {
    //                 dataType=SZ_INT64;
    //             } else {
    //                 usage();
    //             }
    //             break;
    //         case 'i':
    //             if (++i==argc) usage();
    //             inPath=argv[i];
    //             break;
    //         case 'o':
    //             if (++i==argc) usage();
    //             decPath=argv[i];
    //             break;
    //         case 's':
    //             sz2mode=true;
    //             if (++i==argc) usage();
    //             cmpPath=argv[i];
    //             break;
    //         case 'c':
    //             if (++i==argc) usage();
    //             conPath=argv[i];
    //             break;
    //         case '1':
    //             if (++i==argc || sscanf(argv[i], "%zu", &r1) != 1) usage();
    //             break;
    //         case '2':
    //             if (++i==argc || sscanf(argv[i], "%zu", &r1) != 1 || ++i==argc || sscanf(argv[i], "%zu", &r2) != 1)
    //                 usage();
    //             break;
    //         case '3':
    //             if (++i==argc || sscanf(argv[i], "%zu", &r1) != 1 || ++i==argc ||
    //                 sscanf(argv[i], "%zu", &r2) != 1 || ++i==argc || sscanf(argv[i], "%zu", &r3) != 1)
    //                 usage();
    //             break;
    //         case '4':
    //             if (++i==argc || sscanf(argv[i], "%zu", &r1) != 1 || ++i==argc ||
    //                 sscanf(argv[i], "%zu", &r2) != 1 || ++i==argc || sscanf(argv[i], "%zu", &r3) != 1 ||
    //                 ++i==argc || sscanf(argv[i], "%zu", &r4) != 1)
    //                 usage();
    //             break;
    //         case 'M':
    //             if (++i==argc) usage();
    //             errBoundMode=argv[i];
    //             if (i + 1 < argc && argv[i + 1][0] != '-') {
    //                 errBound=argv[++i];
    //             }
    //             break;
    //         case 'A':
    //             if (++i==argc) usage();
    //             absErrorBound=argv[i];
    //             break;
    //         case 'R':
    //             if (++i==argc) usage();
    //             relErrorBound=argv[i];
    //             break;
    //             //            case 'P':
    //             //                if (++i==argc)
    //             //                    usage();
    //             //                pwrErrorBound=argv[i];
    //             //                break;
    //         case 'N':
    //             if (++i==argc) usage();
    //             normErrorBound=argv[i];
    //             break;
    //         case 'S':
    //             if (++i==argc) usage();
    //             psnrErrorBound=argv[i];
    //             break;
    //         default:
    //             usage();
    //             break;
    //     }
    // }

//     if ((inPath==nullptr) && (cmpPath==nullptr)) {
//         printf("Error: you need to specify either a raw binary data file or a compressed data file as input\n");
//         usage();
//         exit(0);
//     }

//     if (!sz2mode && inPath != nullptr && cmpPath != nullptr) {
//         compression=true;
//     }
//     if (cmpPath != nullptr && decPath != nullptr) {
//         decompression=true;
//     }
//     char cmpPathTmp[1024];
//     if (inPath != nullptr && cmpPath==nullptr && decPath != nullptr) {
//         compression=true;
//         decompression=true;
//         snprintf(cmpPathTmp, 1024, "%s.sz.tmp", inPath);
//         cmpPath=cmpPathTmp;
//         delCmpPath=true;
//     }
//     if (inPath==nullptr || errBoundMode==nullptr) {
//         compression=false;
//     }
//     if (!compression && !decompression) {
//         usage();
//         exit(0);
//     }

//     SZ3::Config conf;
//     if (r2==0) {
//         conf=SZ3::Config(r1);
//     } else if (r3==0) {
//         conf=SZ3::Config(r2, r1);
//     } else if (r4==0) {
//         conf=SZ3::Config(r3, r2, r1);
//     } else {
//         conf=SZ3::Config(r4, r3, r2, r1);
//     }
//     if (compression && conPath != nullptr) {
//         conf.loadcfg(conPath);
//     }

//     if (errBoundMode != nullptr) {
//         {
//             // backward compatible with SZ2
//             if (relErrorBound != nullptr) {
//                 conf.relErrorBound=atof(relErrorBound);
//             }
//             if (absErrorBound != nullptr) {
//                 conf.absErrorBound=atof(absErrorBound);
//             }
//             if (psnrErrorBound != nullptr) {
//                 conf.psnrErrorBound=atof(psnrErrorBound);
//             }
//             if (normErrorBound != nullptr) {
//                 conf.l2normErrorBound=atof(normErrorBound);
//             }
//         }
//         if (strcmp(errBoundMode, SZ3::EB_STR[SZ3::EB_ABS])==0) {
//             conf.errorBoundMode=SZ3::EB_ABS;
//             if (errBound != nullptr) {
//                 conf.absErrorBound=atof(errBound);
//             }
//         } else if (strcmp(errBoundMode, SZ3::EB_STR[SZ3::EB_REL])==0 || strcmp(errBoundMode, "VR_REL")==0) {
//             conf.errorBoundMode=SZ3::EB_REL;
//             if (errBound != nullptr) {
//                 conf.relErrorBound=atof(errBound);
//             }
//         } else if (strcmp(errBoundMode, SZ3::EB_STR[SZ3::EB_PSNR])==0) {
//             conf.errorBoundMode=SZ3::EB_PSNR;
//             if (errBound != nullptr) {
//                 conf.psnrErrorBound=atof(errBound);
//             }
//         } else if (strcmp(errBoundMode, SZ3::EB_STR[SZ3::EB_L2NORM])==0) {
//             conf.errorBoundMode=SZ3::EB_L2NORM;
//             if (errBound != nullptr) {
//                 conf.l2normErrorBound=atof(errBound);
//             }
//         } else if (strcmp(errBoundMode, SZ3::EB_STR[SZ3::EB_ABS_AND_REL])==0) {
//             conf.errorBoundMode=SZ3::EB_ABS_AND_REL;
//         } else if (strcmp(errBoundMode, SZ3::EB_STR[SZ3::EB_ABS_OR_REL])==0) {
//             conf.errorBoundMode=SZ3::EB_ABS_OR_REL;
//         } else {
//             printf("Error: wrong error bound mode setting by using the option '-M'\n");
//             usage();
//             exit(0);
//         }
//     }

//     if (compression) {
//         if (dataType==SZ_FLOAT) {
//             compress<float>(inPath, cmpPath, conf);
// #if (!SZ3_DEBUG_TIMINGS)
//         } else if (dataType==SZ_DOUBLE) {
//             compress<double>(inPath, cmpPath, conf);
//         } else if (dataType==SZ_INT32) {
//             compress<int32_t>(inPath, cmpPath, conf);
//         } else if (dataType==SZ_INT64) {
//             compress<int64_t>(inPath, cmpPath, conf);
// #endif
//         } else {
//             printf("Error: data type not supported\n");
//             usage();
//             exit(0);
//         }
//     }
//     if (decompression) {
//         if (printCmpResults && inPath==nullptr) {
//             printf("Error: Since you add -a option (analysis), please specify the original data path by -i <path>.\n");
//             exit(0);
//         }

//         if (dataType==SZ_FLOAT) {
//             decompress<float>(inPath, cmpPath, decPath, conf, binaryOutput, printCmpResults);
// #if (!SZ3_DEBUG_TIMINGS)
//         } else if (dataType==SZ_DOUBLE) {
//             decompress<double>(inPath, cmpPath, decPath, conf, binaryOutput, printCmpResults);
//         } else if (dataType==SZ_INT32) {
//             decompress<int32_t>(inPath, cmpPath, decPath, conf, binaryOutput, printCmpResults);
//         } else if (dataType==SZ_INT64) {
//             decompress<int64_t>(inPath, cmpPath, decPath, conf, binaryOutput, printCmpResults);
// #endif
//         } else {
//             printf("Error: data type not supported\n");
//             usage();
//             exit(0);
//         }
//     }
//     if (delCmpPath) {
//         remove(cmpPath);
//     }
//     return 0;
}
