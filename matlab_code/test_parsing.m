formula = 'aLFuc(1->2)[aDGalNAc(1->3)]bDGal(1->4)bDGlcNAc(1->3)bDGal(1->4)bDGlcNAcOMe';
formula2 = 
%%
g = CGlycan;
g.parse( formula, 1, 'C' );

%%
g.find_mono_by_id( 1 )