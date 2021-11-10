CHAPTERS := logic_gates arithmetic memory architecture

.PHONY: $(CHAPTERS)

.PHONY: all
all: $(CHAPTERS)

# By default just run tests on files with changes.
$(CHAPTERS):
	@cd $@ && $(MAKE) regression

.PHONY: clean
clean:
	$(foreach CHAPTER, $(CHAPTERS), $(MAKE) -C $(CHAPTER) clean;)

# In test mode, always run the tests.
test:
	$(foreach CHAPTER, $(CHAPTERS), $(MAKE) -C $(CHAPTER);)
