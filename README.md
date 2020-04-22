# cs766-virtual-try-on

## todo

- [ ] https://github.com/iamsusmitha/E-Dressing (Paul will try to run this on his laptop)
- [ ] https://github.com/sergeywong/cp-vton (Chia-Wei refactor cp-vton for easier usage)
## timeline
- [ ] 2/21: Read and research some more papers. Create a webpage or a shared media for documenting the project.
- [ ] 3/13: Finish investigations for traditional CV (DRAPE) vs. VITON / VITON-GAN vs. ClothFlow.
- [ ] 3/20: Start some re-implementation of state-of-the-art paper.
- [ ] 3/25: Finish Project Mid-Term Report.
- [ ] 4/10: Finish re-implementation and start evaluation and comparison for different datasets (VITON vs DeepFashion). Find ways to improve existing solutions.
- [ ] 4/27, 4/29, or 5/1: Wrap-up and finish slides for Final Project Presentations
- [ ] 5/4: Finish Project Webpage.

## Quick start
1. make sure you have both pretrain model (see LIP_JPPNet/ & cp-vton/) and store them at right place
2. make sure you can run cp-vton's GMM test & TOM test
3. make sure you can run LIP_JPPNet's evaluate_parsing_JPPNet-s2
4. ./pipeline.sh # this will run an image-cloth pair try on for you