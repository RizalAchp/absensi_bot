
all: build build_single
	%echo "running make.."

build:
	rm -rf ./build
	pyinstaller --distpath ./package ./main.spec

build_single:
	rm -rf ./build
	pyinstaller --distpath ./bin ./single.spec

clean:
	rm -rf ./build
	rm -rf ./bin


