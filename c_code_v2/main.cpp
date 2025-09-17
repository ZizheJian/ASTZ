#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
    char data_path[1024],data_compressed_path[1024],data_decompressed_path[1024];
    char eb_type[10];
    float abs_eb=0,rel_eb=0;
    int FHDE_threshold=0;
    for (int i=1;i<argc;i++)
    {
        if (strcmp(argv[i],"-i") == 0)
        {
            if (i+1<argc)
                strcpy(data_path,argv[++i]);
            else
            {
                fprintf(stderr,"Error: No argument after -i\n");
                return 1;
            }
        }
        else if (strcmp(argv[i],"-z")==0)
        {
            if (i+1<argc)
                strcpy(data_compressed_path,argv[++i]);
            else
            {
                fprintf(stderr,"Error: No argument after -z\n");
                return 1;
            }
        }
        else if (strcmp(argv[i],"-d")==0)
        {
            if (i+1<argc)
                strcpy(data_decompressed_path,argv[++i]);
            else
            {
                fprintf(stderr,"Error: No argument after -d\n");
                return 1;
            }
        }
        else if (strcmp(argv[i],"-o")==0)
        {
            if (i+1<argc)
                strcpy(data_decompressed_path,argv[++i]);
            else
            {
                fprintf(stderr,"Error: No argument after -o\n");
                return 1;
            }
        }
        else if (strcmp(argv[i],"-E")==0)
        {
            if (i+2<argc)
            {
                strcpy(eb_type,argv[++i]);
                if (strcmp(eb_type,"ABS")==0)
                    abs_eb=strtof(argv[++i],NULL);
                else if (strcmp(eb_type,"REL")==0)
                    rel_eb=strtof(argv[++i],NULL);
                else
                {
                    fprintf(stderr,"Error: Unknown error bound type %s\n",eb_type);
                    return 1;
                }
            }
            else
            {
                fprintf(stderr,"Error: Less than 2 arguments after -E\n");
                return 1;
            }
        }
        else if (strcmp(argv[i],"-M")==0)
        {
            if (i+1<argc)
                FHDE_threshold=strtol(argv[++i],NULL,10);
            else
            {
                fprintf(stderr,"Error: No argument after -M\n");
                return 1;
            }
        }
        else
        {
            fprintf(stderr,"Error: Unknown option %s\n",argv[i]);
            return 1;
        }
    }
    printf("Input data path: %s\n", data_path);
    printf("Compressed data path: %s\n", data_compressed_path);
    printf("Decompressed data path: %s\n", data_decompressed_path);
    printf("Error bound type: %s\n", eb_type);
    printf("Absolute error bound: %f\n", abs_eb);
    printf("Relative error bound: %f\n", rel_eb);
    printf("FHDE threshold: %d\n", FHDE_threshold);
}