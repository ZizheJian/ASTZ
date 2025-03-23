#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "Config.hpp"

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
    printf("* configuration file: \n");
    printf("    -c <configuration file>: configuration file\n");
    printf("* topology list file:\n");
    printf("    -t <topology list file>: topology list file\n");
    printf("* error control:\n");
    printf("    -E <error control mode> <error bound (optional)>\n");
    printf("    error control mode as follows:\n");
    printf("        REL (value range based error bound, so a.k.a., VR_REL)\n");
    printf("    error bound can be set directly after the error control mode, or separately with the following options:\n");
    printf("        -R <value_range based relative error bound>: specifying relative error bound\n");
    printf("* method:\n");
    printf("    -M <method> <threshold (optional)>\n");
    printf("    method as follows:\n");
    printf("        HDE (Hyper-Determined Equation)\n");
    printf("        FHDE <threshold> (Filtered Hyper-Determined Equation)\n");
    printf("* dimensions:\n");
    printf("    -3 <nx> <ny> <nz>: dimensions for 3D data such as data[nz][ny][nx]\n");
    exit(0);
}

int main(int argc,char **argv)
{
    int print_analysis_results=0;
    bool compression=false;
    bool decompression=false;
    char *in_path=nullptr;
    char *cmp_path=nullptr;
    char *cfg_path=nullptr;
    char *topology_path=nullptr;
    char *decmp_path=nullptr;
    bool del_cmp_path=false;

    char *eb_mode=nullptr;
    char *eb=nullptr;
    char *rel_eb=nullptr;

    char *method=nullptr;
    char *threshold=nullptr;

    size_t r3=0;
    size_t r2=0;
    size_t r1=0;

    size_t i=0;
    if (argc==1)    usage();
    int width=-1;
    for (i=1;i<argc;i++)
   {
        if ((argv[i][0]!='-') || (argv[i][2]))  usage();
        switch (argv[i][1]){
            case 'h':   usage();
            case 'a':
                print_analysis_results=1;
                break;
            case 'z':
                compression=true;
                if (i+1<argc)
               {
                    cmp_path=argv[i+1];
                    if (cmp_path[0]!='-')
                        i++;
                    else
                        cmp_path=nullptr;
                }
                break;
            case 'f':   break;
            case 'i':
                if (++i==argc)  usage();
                in_path=argv[i];
                break;
            case 'o':
                if (++i==argc)  usage();
                decmp_path=argv[i];
                break;
            case 'c':
                if (++i==argc)  usage();
                cfg_path=argv[i];
                break;
            case 't':
                if (++i==argc)  usage();
                topology_path=argv[i];
                break;
            case '3':
                if (++i==argc || sscanf(argv[i],"%zu",&r1)!=1 || ++i==argc ||
                    sscanf(argv[i],"%zu",&r2)!=1 || ++i==argc || sscanf(argv[i],"%zu",&r3)!=1)
                    usage();
                break;
            case 'E':
                if (++i==argc)  usage();
                eb_mode=argv[i];
                if (i+1<argc && argv[i+1][0]!='-')  eb=argv[++i];
                break;
            case 'R':
                if (++i==argc)  usage();
                rel_eb=argv[i];
                break;
            case 'M':
                if (++i==argc)  usage();
                method=argv[i];
                if (strcmp(method,"FHDE")==0)
                    if (i+1<argc && argv[i+1][0]!='-')
                        threshold=argv[++i];
                    else
                        usage();
                break;
            default:
                usage();
                break;
        }
    }

    if ((in_path==nullptr) && (cmp_path==nullptr))
    {
        printf("Error: you need to specify either a raw binary data file or a compressed data file as input\n");
        usage();
    }
    if (topology_path==nullptr)
    {
        printf("Error: you need to specify a topology list file\n");
        usage();
    }

    if ((in_path!=nullptr) && (cmp_path!=nullptr))  compression=true;
    if ((cmp_path!=nullptr) && (decmp_path!=nullptr))   decompression=true;
    char cmp_path_tmp[1024];
    if ((in_path!=nullptr) && (cmp_path==nullptr) && (decmp_path!=nullptr))
    {
        compression=true;
        decompression=true;
        snprintf(cmp_path_tmp,1024,"%s.fhde.tmp",in_path);
        cmp_path=cmp_path_tmp;
        del_cmp_path=true;
    }
    if (in_path==nullptr)   compression=false;
    if ((!compression) && (!decompression)) usage();

    FHDE::Config conf=FHDE::Config(r3,r2,r1);
    if (eb_mode!=nullptr)
    {
        conf.rel_eb=atof(rel_eb);
        conf.eb_mode=FHDE::EB_REL;
    }

//     if (compression){
//         if (dataType==SZ_FLOAT){
//             compress<float>(in_path,cmp_path,conf);
// #if (!SZ3_DEBUG_TIMINGS)
//         } else if (dataType==SZ_DOUBLE){
//             compress<double>(in_path,cmp_path,conf);
//         } else if (dataType==SZ_INT32){
//             compress<int32_t>(in_path,cmp_path,conf);
//         } else if (dataType==SZ_INT64){
//             compress<int64_t>(in_path,cmp_path,conf);
// #endif
//         } else{
//             printf("Error: data type not supported\n");
//             usage();
//             exit(0);
//         }
//     }
//     if (decompression){
//         if (print_analysis_results && in_path==nullptr){
//             printf("Error: Since you add -a option (analysis),please specify the original data path by -i <path>.\n");
//             exit(0);
//         }

//         if (dataType==SZ_FLOAT){
//             decompress<float>(in_path,cmp_path,decmp_path,conf,binaryOutput,print_analysis_results);
// #if (!SZ3_DEBUG_TIMINGS)
//         } else if (dataType==SZ_DOUBLE){
//             decompress<double>(in_path,cmp_path,decmp_path,conf,binaryOutput,print_analysis_results);
//         } else if (dataType==SZ_INT32){
//             decompress<int32_t>(in_path,cmp_path,decmp_path,conf,binaryOutput,print_analysis_results);
//         } else if (dataType==SZ_INT64){
//             decompress<int64_t>(in_path,cmp_path,decmp_path,conf,binaryOutput,print_analysis_results);
// #endif
//         } else{
//             printf("Error: data type not supported\n");
//             usage();
//             exit(0);
//         }
//     }
//     if (del_cmp_path){
//         remove(cmp_path);
//     }
//     return 0;
}
