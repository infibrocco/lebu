#include <stdio.h>
#include <stdlib.h>

int fib(int n);

int main(int argc, char** argv)
{
	printf("%d\n", fib(atoi(argv[1])));
	//printf("hell0 wrld!!\n");
	return 0;
}