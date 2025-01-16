#include<stdio.h>
#include<stdlib.h>
#include<math.h>

int gcd(int a, int b) {
    if (b == 0) {
        return a;
    } else {
        return gcd(b, a % b);
    }
}
int lcm(int a, int b) {
    return a * b / gcd(a, b);
}


int main(){
    int p=0,v=0,k=0;
    int a=0,b=0,c=0,d=0;
    int n=0;
    scanf("%d %d %d",&p,&v,&k);
    b = lcm(p+1,c+1); //도색도 광택도 되지 않은 연필의 수
    a = k-b; //완료된 연필의 수
    d = k/(p+1)-b; //광택이 되지 않은 연필의 수
    c = k/(v+1)-b; //도색이 되지 않은 연필의 수​
    printf("%d %d %d %d\n",a,b,c,d);
}