#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define SVPNG_PUT(u)\
    fputc(u,fp)
#define SVPNG_U8A(ua,l)\
    for (i=0;i<l;i++)\
        SVPNG_PUT((ua)[i]);
#define SVPNG_U32(u)\
    SVPNG_PUT((u)>>24);\
    SVPNG_PUT(((u)>>16)&255);\
    SVPNG_PUT(((u)>>8)&255);\
    SVPNG_PUT((u)&255);
#define SVPNG_U8C(u)\
{\
    SVPNG_PUT(u);\
    c^=(u);\
    c=(c>>4)^t[c&15];\
    c=(c>>4)^t[c&15];\
}
#define SVPNG_U8AC(ua,l)\
    for (i=0;i<l;i++)\
        SVPNG_U8C((ua)[i])
#define SVPNG_U16LC(u)\
    SVPNG_U8C((u)&255);\
    SVPNG_U8C(((u)>>8)&255);
#define SVPNG_U32C(u)\
    SVPNG_U8C((u)>>24);\
    SVPNG_U8C(((u)>>16)&255);\
    SVPNG_U8C(((u)>>8)&255);\
    SVPNG_U8C((u)&255);
#define SVPNG_U8ADLER(u)\
{\
    SVPNG_U8C(u);\
    a=(a+(u))%65521;\
    b=(b+a)%65521;\
}
#define SVPNG_BEGIN(s,l)\
    SVPNG_U32(l);\
    c=~0U;\
    SVPNG_U8AC(s,4);
#define SVPNG_END()\
    SVPNG_U32(~c)

void output_png(FILE *fp,unsigned int w,unsigned int h,unsigned char *img)
{
    unsigned t[]={0,0x1db71064,0x3b6e20c8,0x26d930ac,0x76dc4190,0x6b6b51f4,0x4db26158,0x5005713c,
            0xedb88320,0xf00f9344,0xd6d6a3e8,0xcb61b38c,0x9b64c2b0,0x86d3d2d4,0xa00ae278,0xbdbdf21c};
    unsigned int a=1;
    unsigned int b=0;
    unsigned int p=w*3+1;
    unsigned int c,i;

    SVPNG_U8A("\x89PNG\r\n\32\n",8);
    SVPNG_BEGIN("IHDR",13);
    SVPNG_U32C(w);
    SVPNG_U32C(h);
    SVPNG_U8C(8);
    SVPNG_U8C(2);
    SVPNG_U8AC("\0\0\0",3);
    SVPNG_END();
    SVPNG_BEGIN("IDAT",2+h*(5+p)+4);
    SVPNG_U8AC("\x78\1",2);
    for (unsigned int y=0;y<h;y++)
    {
        SVPNG_U8C(y==h-1);
        SVPNG_U16LC(p);
        SVPNG_U16LC(~p);
        SVPNG_U8ADLER(0);
        for (unsigned int x=0;x<p-1;x++)
            SVPNG_U8ADLER(img[y*(p-1)+x]);
    }
    SVPNG_U32C((b<<16)|a);
    SVPNG_END();
    SVPNG_BEGIN("IEND",0);
    SVPNG_END();
}

//将输入x(值域[-1,1])当做hsv的h，转换成rgb
void h2rgb(float x,unsigned char *r,unsigned char *g,unsigned char *b)
{
    if (x>1)
        x=1;
    if (x<-1)
        x=-1;
    float h=5*(x+1)/12;
    int i;
    float f;
    h*=6;
    i=(int)h;
    f=h-i;
    switch (i) {
        case 0:
            *r=255;
            *g =(unsigned char)(f*255);
            *b=0;
            break;
        case 1:
            *r=(unsigned char)((1-f)*255);
            *g=255;
            *b=0;
            break;
        case 2:
            *r=0;
            *g=255;
            *b=(unsigned char)(f*255);
            break;
        case 3:
            *r=0;
            *g=(unsigned char)((1-f)*255);
            *b=255;
            break;
        case 4: 
            *r=(unsigned char)(f*255);
            *g=0;
            *b=255;
            break;
        default:
            *r=255;
            *g=0;
            *b=(unsigned char)((1-f)*255);
            break;
    }
}

//将输入x(值域[-1,1])线性转换成红或蓝，x=1为红，x=-1为蓝
void h2rb(float x,unsigned char *r,unsigned char *g,unsigned char *b)
{
    if (x>1)
        x=1;
    if (x<-1)
        x=-1;
    if (x>=0)
    {
        *r=255;
        *g=255-255*x;
        *b=255-255*x;
    }
    else
    {
        *r=255+255*x;
        *g=255+255*x;
        *b=255;
    }
}

//将输入x(值域[-32767,32767])对数转换成红或蓝，x=32767为红，x=-32767为蓝
void h2log2rb(float x,unsigned char *r,unsigned char *g,unsigned char *b)
{
    if (x>=0)
        x=log2(x+1)/10;
    else
        x=-log2(-x+1)/10;
    if (x>1.5)
        x=1.5;
    if (x<-1.5)
        x=-1.5;
    if (x>1)
    {
        *r=510-255*x;
        *g=0;
        *b=0;
    }
    else if (x<-1)
    {
        *r=0;
        *g=0;
        *b=510+255*x;
    }
    else
        h2rb(x,r,g,b);
}

//接收两个二维数组，第一个值域为[-1,1]，作为hsv的h。第二个值域为{0,1,2}，0表示使用h2rgb，1表示使用h2rb，2表示h2log2rb
void plot(const char *png_path,float *fig,int *plot_type,int h,int w,int hn,int wn)
{
    unsigned char *img=(unsigned char*)malloc(h*w*hn*wn*3);
    for (int hid=0;hid<hn;hid++)
        for (int wid=0;wid<wn;wid++)
        {
            if (plot_type[hid*wn+wid]==0)
                for (int i=0;i<h;i++)
                    for (int j=0;j<w;j++)
                    {
                        int pos=(hid*h+i)*w*wn+wid*w+j;
                        h2rgb(fig[pos],img+3*pos,img+3*pos+1,img+3*pos+2);
                    }
            if (plot_type[hid*wn+wid]==1)
                for (int i=0;i<h;i++)
                    for (int j=0;j<w;j++)
                    {
                        int pos=(hid*h+i)*w*wn+wid*w+j;
                        h2rb(fig[pos],img+3*pos,img+3*pos+1,img+3*pos+2);
                    }
            if (plot_type[hid*wn+wid]==2)
                for (int i=0;i<h;i++)
                    for (int j=0;j<w;j++)
                    {
                        int pos=(hid*h+i)*w*wn+wid*w+j;
                        h2log2rb(fig[pos],img+3*pos,img+3*pos+1,img+3*pos+2);
                    }
        }
    FILE *f=fopen(png_path,"wb");
    if (f==NULL)
    {
        printf("Error: %s open failed\n",png_path);
        return;
    }
    output_png(f,w*wn,h*hn,img);
    fclose(f);
    free(img);
}