classdef CGlycan < handle % By Pengyu Hong @ Brandeis University
    properties
        mStem = [];
        mBranches = CGlycan.empty(0.0);
        mFormula = '';

        mMass = 0;

        mReducingEndModification = '';
    end
    
    methods(Static)
        function [stem_formula, branch_formulas] = break_formula( formula, sorted )
            if nargin < 2
                sorted = 0;
            end

            formula = strtrim( formula );
            
            % find branching points
            branch_pos = []; num = 0;            
            for k = length( formula ) : -1 : 1
                if formula(k) == ']'
                    if num == 0
                        branch_pos(2,end+1) = k-1;
                    end
                    num = num + 1;
                elseif formula(k) == '['
                    num = num - 1;
                    if num == 0
                        branch_pos(1,end) = k+1;
                    end
                elseif num == 0 && ~isempty(branch_pos)
                    break;
                end
            end
            if num ~= 0, throw( MExeption( 'CGlycan.parse', 'Wrong formula: mis-matched [-].') ); end

            if ~isempty(branch_pos) && branch_pos(1,end) ~= 1
                branch_pos(2,end+1) = branch_pos(1,end) - 2;
                branch_pos(1,end) = 1;
            end
            
            % pre-assign the stem, will be changed later.
            if ~isempty( branch_pos )
                stem_formula = strtrim( formula( branch_pos(2,1)+2 : end) );
            else
                stem_formula = formula;
            end
            
            % get branch formula
            branch_formulas = cell( 1, size( branch_pos, 2 ) );
            if ~isempty( branch_pos )
                for k = 1 : size( branch_pos, 2 )
                    branch_formulas{k} = strtrim( formula( branch_pos(1, k) : branch_pos(2, k) ) );
                end
            end

            % order branch formula by their linkage
            if sorted
                num = length( branch_formulas );
                linkage = cell(1, num);
                for k = 1 : num
                    linkage{k} = branch_formulas{k}(end);
                end
                [~, inds] = sort( linkage );
                branch_formulas = branch_formulas( inds );
            end
        end

    end
    
    methods
        function obj = CGlycan( permethylation, reducingEndModification )
        % function obj = CGlycan( permethylation, reducingEndModification )
            if nargin >= 1
                if ~isempty( permethylation )
                    obj.mPermethylated = permethylation;
                end
                if nargin >= 2 && ~isempty( reducingEndModification )
                    obj.mReducingEndModification = reducingEndModification;
                end
            end
        end
        
        function mono = find_mono_by_id(obj, id)
            mono = [];
            if id < 0, return; end
            
            for k = 1 : length( obj.mStem )
                if obj.mStem(k).ID == id
                    mono = obj.mStem(k); 
                    return;
                end
            end
            
            for k = 1 : length( obj.mBranches )
                mono = obj.mBranches(k).find_mono_by_id( id );
                if ~isempty( mono ) 
                    return; 
                end
            end
        end
        
        function nodeID = parse( obj, formula, startNodeID, format )
            if nargin < 3 || isempty(startNodeID), startNodeID = 1; end
            
            obj.mFormula = formula;

            if startNodeID == 1 && format == 'C'
                formula = strrep(formula, '->', '-');
                formula = strrep(formula, '(', '');
                formula = strrep(formula, ')', '');
            end

            obj.mStem = []; obj.mBranches = [];
            
            % find branching points
            [stem_formula, branch_formulas] = CGlycan.break_formula( formula );
            
            % parse the stem
            stem_formula = strtrim( stem_formula );
            units = strsplit( stem_formula, '-' );
            units = fliplr( units );
            
            linkedTo = -1; % initialize linkedTo for the first monosaccharide in the stem
            % 
            if startNodeID == 1
                if format == 'C'
                    if endsWith( units{1}, 'OH' )
                        obj.mReducingEndModification = 'OH';
                        units{1} = units{1}(1:end-2);
                    elseif endsWith( units{1}, 'OMe')
                        obj.mReducingEndModification = 'OMe';
                        units{1} = units{1}(1:end-3);
                    end
                elseif length( units{1} ) < 4
                    obj.mReducingEndModification = units{1};
                    units = units(2:end);
                end
            elseif length( units{1} ) == 1 && units{1} >= '2' && units{1} <= '9'
                linkedTo = str2num( units{1} );
                units = units(2:end);
            end

            obj.mStem = [];
            nodeID = startNodeID;
            for k = 1 : length( units )
                temp = units{k};
                if temp(end) >= '1' && temp(end) <= '9'
                    temp = temp(1:end-1);
                end
                obj.mStem(k).ID = nodeID;
                obj.mStem(k).linkedTo = linkedTo;

                if temp(1) >= '1' && temp(1) <= '9'
                    linkedTo = str2num( temp(1) );
                    if format == 'C'
                        obj.mStem(k).anomer = temp(2);
                        obj.mStem(k).monosaccharide = temp(3:end);
                    else
                        obj.mStem(k).monosaccharide = temp(2:end-1);
                        obj.mStem(k).anomer = temp(end);
                    end
                else
                    linkedTo = -1;
                    if format == 'C'
                        obj.mStem(k).anomer = temp(1);
                        obj.mStem(k).monosaccharide = temp(2:end);
                    else
                        obj.mStem(k).monosaccharide = temp(1:end-1);
                        obj.mStem(k).anomer = temp(end);
                    end
                end

                nodeID = nodeID + 1;
            end
            
            % parse the branches
            if isempty( branch_formulas )
                obj.mBranches = CGlycan.empty(0,0);
            else
                obj.mBranches = CGlycan.empty(0, length(branch_formulas));
                for k = 1 : length( branch_formulas ) 
                    % parse a branch
                    obj.mBranches(k) = CGlycan;
                    nodeID = obj.mBranches(k).parse( branch_formulas{k}, nodeID, format );
                end
            end
        end
    end
end