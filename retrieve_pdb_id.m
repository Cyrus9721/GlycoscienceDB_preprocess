% @Author  : Zizhang Chen
% @Contact : zizhang2@outlook.com
max_numglycan = 30;
a = readtable('pdb_name.csv');
formulas = a.formula;

mat_label = strings(length(formulas), max_numglycan);

for i = 1:length(formulas)
    temp_formula = formulas{i};
    g = CGlycan;
    if strcmp(temp_formula,'Missing formula')
        continue
    end
    g.parse( temp_formula, 1, 'C' );
    disp(temp_formula);
    for j = 1:max_numglycan
        temp_mono_obj = g.find_mono_by_id( j );
        temp_mono = 'wierd';
        if isempty(temp_mono_obj)
            temp_mono = NaN;
        else
            temp_mono = temp_mono_obj.monosaccharide;
        end
        mat_label(i, j) = temp_mono;
    end
    clear g
end
writematrix(mat_label, 'labeled.csv');
