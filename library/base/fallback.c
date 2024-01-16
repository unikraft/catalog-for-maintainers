#include <stdio.h>

int main(int argc, char *argv[]) {
	printf(
		"  .--------------------.\n"
		" ( Hello from Unikraft! )\n"
		"  '--------------------'\n"
		"         \\\n"
		"          \\\n"
		"             _\n"
		"           c'o'o  .--.\n"
		"           (| |)_/\n"
		"\n"
		"\n"
		"This is the default message when no root filesystem is supplied to this\n"
		"'base' image.  This 'base' image is a general-purpose unikernel runtime\n"
		"and is intended to be used for your application.\n"
		"\n"
		"To use this 'base' image, place a `Kraftfile` in your application\n"
		"repository.  For example:\n"
		"\n"
		"\t```yaml\n"
		"\tspec: v0.6\n"
		"\truntime: unikraft.org/base:latest\n"
		"\trootfs: ./Dockerfile\n"
		"\t```\n"
		"\n"
		"In the above example, you can supply this 'base' image with your own \n"
		"root filesystem.  This filesystem is defined through the `Dockerfile`.\n"
		"Once setup, simply call:\n"
		"\n"
		"\t```bash\n"
		"\tkraft run .\n"
		"\t```\n"
		"\n"
		"For more information, how to get started and examples using this 'base'\n"
		"image, please visit:\n"
		"\n"
		"\thttps://unikraft.org/guides/intro-to-base-image\n"
		"\n"
		"Happy krafting!\n"
		"\n"
	);

	return 0;
}
