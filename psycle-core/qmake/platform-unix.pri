unix {
	message("System is: unix.")
	TOP_SRC_DIR = $$system(cd .. && pwd)
}
