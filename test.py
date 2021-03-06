from subprocess import Popen, PIPE
import os
import copy
import Bio
from Bio import SeqIO,AlignIO
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import numpy as np
import random

class Check_files():
    '''Check all input files/dependencies/etc. are in the accessible/in the working directory
    '''
    def __init__(self):
        #List input files that need to exist before running.
        #Useful to avoid hardcoded paths. 
        path=os.getcwd()+'/'
        self.cwd=path
    def file_exists(self,f):
        #check if a while exists
        if os.path.isfile(f):
            return True
        else:
            print ("Fatal: File not found",f)
            exit()
        return False
    def execs_exist(self):
        #list of executables
        #add matlab to this execlist (but keep in mind that matlab is not working on this system without changing into its executable directory)
        import distutils
        x=[]
        execlist=['hmmbuild']
        for i in execlist:
            x+=distutils.spawn.find_executable(i)
        if False in X:
            print ("One of the required programs is missing")
            exit()
    #I don't think we're using the below two functions anywhere
    def common_files(self):
        cwd=self.cwd
        a,b,c,d=common_files()
        return cwd+a,cwd+b,cwd+c,cwd+d
    def specific_files(self,filename):
        cwd=self.cwd
        a,b,c,d,e,f=specific_files(filename)
        return cwd+a,cwd+b,cwd+c,cwd+d,cwd+e,cwd+f

    #check if family is downloaded
    def fam_exist(self,accession):
        x=self.cwd+'families/'+accession+'.fasta'
        #print (x)
        return os.path.exists(x)

    #write sequences in list format to a fasta file
    def list_to_file(self,list1,outfile):
        #print (">>list_to_file: Write fasta.\n",outfile)
        with open(outfile, 'w+') as f:
            for item in list1:
                f.write("%s\n" % item)
        f.close()        
        return                

class Alignment():
    '''
    Class for performing string manipulation and alignments.
    Are all the infile and outfile variables for methods the same strings? 
    remove_dashes,cdhit,fasta_to_x,
    Alignment for one family.
    '''
    
    def __init__(self):
        #self.in_file=in_file
        #self.out_file=out_file
        self.amino_acids=['-','A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y']
        return

    #input fasta file and return - list of sequences, list of headers and number of sequences
    def family_to_string(self,fam_file):
        #print (">>Alignment:family_to_string:",fam_file,"\n")
        #Read all sequences in fasta family file and return all proteins as list of strings.
        fasta_sequences = SeqIO.parse(open(fam_file),'fasta')
        seqlist=[];idlist=[]
        for i in fasta_sequences:
            name, sequence = i.id, i.seq
            seqlist+=[list(sequence)]
            idlist+=[name]
        numseq=len(seqlist)
        #print ("Read",numseq,"sequences from file",fam_file,"\n")
        return idlist,seqlist,numseq

    def remove_dashes_list(self,wd):
        #print (">>Alignment:remove_dashes_list")
        #wd: list of strings with dashes
        #wod: list of strings without dashes.
        wod=[]
        seq_length=[]
        for i in wd:
            j=''.join(i).replace("-","") 
            wod+=[j];seq_length+=[len(j)]
            assert (j.isalpha()),'Error: Non-alphabet found in family'
        num_seq=len(seq_length)        
        return wod,num_seq

    # this does the exact opposite job of the fasta to list function
    def write_fasta(self,idlist,seqlist,fastafile):
        #print (">>Alignment:write_fasta\n",fastafile)
        f = open(fastafile,"w+")
        #Write fasta file from ids and protein sequence list.
        assert(len(idlist)==len(seqlist)),'Idlist and sequence list do not match'
        for i in range(0,len(idlist)):
            id='>'+idlist[i];seq=''.join(seqlist[i])
            f.write('%s\n' % (id))
            f.write('%s\n' % (seq))

        f.close()
        return

    #align a fasta file with multiple protein sequences using mafft
    def fasta_to_mafft(self,in_file, out_file):
        #print (">>Alignment:fasta_to_mafft\n",in_file,out_file)
        f=open(out_file,"w+")
        p=Popen(['mafft',in_file],stdout=f,stderr=PIPE)
        stdout, stderr = p.communicate();p.wait();f.close()
        return stdout,stderr
    #alignment using clustalo
    def fasta_to_clustalo(self, in_file, out_file):
        f = open(out_file, "w+")
        p = Popen(['clustalo', '-i', in_file], stdout = f, stderr = PIPE)
        stdout, stderr = p.communicate();p.wait();f.close()
        return stdout, stderr

    #cd-hit clustering to remove very similar sequences
    def cdhit(self,in_file, out_file):
        #cmd = 'cd-hit -i ' + in_file + ' -o ' + out_file + ' -T 1 -c 0.90'
        process=Popen(['cd-hit','-i',in_file,'-o',out_file,'-T','1','-c','0.90'],stdout=PIPE,stderr=PIPE)
        stdout, stderr = process.communicate()
        process.wait()
        return stdout,stderr

    def sequence_length_dist(self,seqlist):
        #print (">>Aligment:sequence_length_dist\n")
        #Get sequence length distribution from sequencelist
        seq_length_list=[]
        for i in seqlist:
            seq_length_list+=[len(i)]
    #    print (seq_length_list)
        return seq_length_list
    def plot_length_dist(self,seq_length_list,name):
        x=np.arange(1,len(seq_length_list)+1,1)
        plt.scatter(x,seq_length_list)        
        plt.savefig(name+'.pdf')        

    def mode_of_list(self,sequence_lengths):
        #print (">>Alignment:mode_of_list\n")
        n = len(sequence_lengths)
        data = Counter(sequence_lengths) 
        get_mode = dict(data) 
        mode = [k for k, v in get_mode.items() if v == max(list(data.values()))]
        if n == len(mode):
                return None
        else:
                return mode
    def realign(self,original_alignment,hmm_sequences, out_file):
        #print (">>Alignment:realign",original_alignment,hmm_sequences,out_file)
        f=open(out_file,"w+")
        p=Popen(['mafft','--add',hmm_sequences,'--reorder','--keeplength',original_alignment],stdout=f,stderr=PIPE)
        p.wait();stderr, stdout = p.communicate();f.flush();f.close()
        #print (stderr)
        return stdout

    def split_combined_alignment(self, combined_alignment_file, hmm_emitted_file_aligned):
        #print('>>Alignment:split_combined_alignment')
        hmm_sequences_records = []
        with open(hmm_emitted_file_aligned, 'w') as fin:
            for record in SeqIO.parse(combined_alignment_file, 'fasta'):
                if 'refined' in record.id:
                    hmm_sequences_records.append(record)
        SeqIO.write(hmm_sequences_records, hmm_emitted_file_aligned, 'fasta')

class Consensus(object):
    '''
    Class containing various methods of finding a consensus sequence for one family.
    Should become its own module in due course.
    Should we pass 'sequences' as an instance for the entire Consensus class?
    '''
    def __init__(self):
        self.amino_acids=['-','A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y']
        #self.sequences=sequences
        return
    def check_break_conditions(self,num_seq,loa1,loa0,mode,count):
        bools=[False,False,False,False,False]
        print ('>>Consensus:check_break_conditions')
        #Add any number of conditions here
        #condition
        print (num_seq) 
        c1=(num_seq<520)
        #condition 2
        x = 0.1*mode[0]
        y1 = mode[0] - x; y2=mode[0]+x
        c21=(loa1<y1);c22=(loa1>y2)
        #Condition3
        c3=(loa1==loa0) 
        c4=(count>1000)#adding for testing
        if c4:
            print ("Fatal: Maximum number of iterations exceeded",count)
            exit()
        bools=[c1,c21,False,False,c4]
        print (bools)

        return c3,bools
    def profile_matrix(self,sequences):
        #print (">>Consensus:profile_matrix")
        #print (sequences)
        sequence_length = len(sequences[0]) #length of first sequences (length of allsequences is the same after alignment)
        profile_matrix = {} #profile matrix in dictionary format
        for acid in self.amino_acids:
                profile_matrix[acid] = [float(0) for i in range(sequence_length)] #initialise all entries in profile matrix to zero
        for i in range(len(sequences)):
                seq = sequences[i].upper() #convert sequence to upper case, just in case it isn't
                for j in range(len(seq)): #for each letter in the sequence
                    profile_matrix[seq[j]][j] += float(1) #increase frequency of the letter (seq[j]) at position j
        for aa in profile_matrix: #for amino acid in profile matrix
                l = profile_matrix[aa] #l i sthe list of frequencies associated with that amino acid
                for i in range(len(l)): #for position i in l
                        l[i] /= float(len(sequences)) #divide frequency at i by the length of the list l
        pm = OrderedDict([(x, profile_matrix[x]) for x in self.amino_acids])
        return pm

    def get_all_indices(self,l, value):
        return [i for i, val in enumerate(l) if val == value]
    '''
    def consensus_sequence_nd(self,pm,sequences):
       print (">>Consensus:consensus_sequence_nd: No dashes in consensus")
        consensus_seq = ''
        sequence_length = len(sequences[0])
        for i in range(sequence_length):
            l = []
            for aa in pm:
               l.append(pm[aa][i])
            max_value = max(l)
            indices = self.get_all_indices(l, max_value)
            index = indices[0]
            if self.amino_acids[index] == '-':
                if l[index] < 0.5:
                    second_largest_value = self.second_largest(l)
                    if second_largest_value == max_value:
                        index = indices[1]
                    else:
                        index = l.index(second_largest_value)
                else:
                    continue
            consensus_seq += self.amino_acids[index]

        return consensus_seq
    '''
    #finding second largest number in a list(found this on stack overflow)
    def second_largest(self,numbers):
        count = 0
        m1 = m2 = float('-inf')
        for x in numbers:
                count += 1
                if x > m2:
                        if x >= m1:
                                m1, m2 = x, m1
                        else:
                                m2 = x

        return m2 if count >= 2 else None

    '''
    def consensus_sequence(self,sequences, pm):
    #find consensus sequence from sequences in list format (with dashes)
        consensus_seq = ''
        #pm = profile_matrix(sequences)
        sequence_length = len(sequences[0]) #length of any sequence
        for i in range(sequence_length):
                l = []
                for aa in pm:
                        l.append(pm[aa][i]) #list of probabilities of amino acid 'aa' at every position
                max_value = max(l) #find maximum value in the above list
                indices = self.get_all_indices(l, max_value) #get all indices in the list which have the above maximum value
                index = indices[0] #get first index
            
                if self.amino_acids[index] == '-': #if amino acid at that index is a dash
                        if l[index] < 0.5: #if probability of occurence of dash is less than 0.5
                                second_largest_value = self.second_largest(l) #then find the second largest value
                                if second_largest_value == max_value: #if second largest and largest and largest values are equal, then get the second index from the list of max values
                                        index = indices[1]
                                else:
                                    index = l.index(second_largest_value) #get index of amino acid with second largest probability of occurence (after dash)
                        #else:
                        #        continue #if probability of occurence of dash is greater than 0.5 then skip adding an amino acid at that position

                consensus_seq += self.amino_acids[index] #append amino acid to consensus sequence

        return consensus_seq
    '''

    #find a consensus sequences with or without dashes
    #check out the abovr commented function for more comments
    def find_consensus_sequence(self,sequences,pm,option):
        #print(sequences)
        consensus_seq=''
        sequence_length=len(sequences[0])
        for pos in range(sequence_length):
            l=[]
            for aa in pm:
                l.append(pm[aa][pos])
            max_value=max(l)
            indices=self.get_all_indices(l,max_value)
            index_max_value=indices[0]
            if self.amino_acids[index_max_value]=='-':
                if l[index_max_value]<0.5:
                    second_largest_value=self.second_largest(l)
                    if second_largest_value==max_value:
                        index_max_value=indices[1]
                    else:
                        index_max_value=l.index(second_largest_value)
                else:
                    if option==1:
                        continue
            consensus_seq+=self.amino_acids[index_max_value]
        return consensus_seq
    '''
    def consensus_with_dashes_no_realign(self,sequences,pm):
        print(">>Consensus:consensus with dashes, no realignment")
        cs=find_consensus_sequence(self,sequences,pm,2)
        return cs
    '''
    def realign_consensus_to_alignment(self,alignment,consensus_temp,consensus_aln_temp):
        fout=open(consensus_aln_temp,"w+")
        p=Popen(['mafft','--add',consensus_temp,'--keeplength',alignment],stdout=fout,stderr=PIPE)
        p.wait();stderr,stdout=p.communicate();fout.flush();fout.close()
        return stdout

    def find_consensus_from_realigned_file(self,consensus_aln_temp):
        cs=''
        for record in SeqIO.parse(consensus_aln_temp,'fasta'):
            if 'consensus' in record.id:
                cs=str(record.seq)
        return cs

    def consensus_without_dashes_realign(self,cs,alignment,consensus_temp,consensus_aln_temp):
        #print(">>Consensus:consensus without dashes, realignment with given alignment(either refined or hmm)")
        with open(consensus_temp,'w') as f:
            f.write('>consensus_from_alignment\n')
            f.write(cs)
        self.realign_consensus_to_alignment(alignment,consensus_temp,consensus_aln_temp)
        cs=self.find_consensus_from_realigned_file(consensus_aln_temp)
        return cs

    #finding index of bad sequence numbers in the sequence list
    def find_bad_sequences(self,profile_matrix, sequences, name_list):
        print (">>Consensus:find_bad_sequences")
        max_value = max(profile_matrix['-']) #max probability of finding a dash
        if max_value == 1: #just in case there are dashes in every sequence at that position
                max_value = second_largest(profile_matrix['-'])
        positions = [] 
        for i in range(len(profile_matrix['-'])):
                if profile_matrix['-'][i] == max_value: #all positions at which probability of finding a dash is maximum
                        positions.append(i)
        bad_sequence_numbers = []
        for i in range(len(sequences)):
                for position in positions:
                        if sequences[i][position] != '-': #if sequence does not have a dash at the position where probability of finding a dash is the maximum
                                if i not in bad_sequence_numbers: #if sequence is not already in the list
                                        bad_sequence_numbers.append(i)
        return bad_sequence_numbers
    def remove_bad_sequences(self,sequences, name_list, bad_sequence_numbers):
        print (">>Consensus:bad_sequence_numbers")
        sequences = [x for i, x in enumerate(sequences) if i not in bad_sequence_numbers]
        name_list = [x for i, x in enumerate(name_list) if i not in bad_sequence_numbers]
        return sequences, name_list
                
    def sequencestr_to_seq_list(self,sequence):
        #Convert conensus.py sequence variable (list of strings) to (list of lists). 
        j=[]
        for i in sequence:
            j+=[list(i)]
        return j
    def copy_file(self,f1,f2):
        p=Popen(['cp','-r',f1,f2],stdin=PIPE,stdout=PIPE)
        stdout,stderr=p.communicate()
        p.wait()
        return

    def shuffle_consensus(self,cs):
        cs = list(cs)
        for i in range(len(cs)):
            j = random.randint(i, len(cs) - 1)
            cs[i], cs[j] = cs[j], cs[i]
        cs = ''.join(cs)
        return cs
            
    def iterate(self,mode,idlist,seqlist,num_seq,seq_length_list,write_file,refined_file,temp_file,out_file,final_consensus_file,profile_hmm_file,hmm_emitted_file,combined_alignment_file, hmm_emitted_file_aligned,consensus_temp,consensus_aln_temp,option,hmm_consensus_file):
        #idlist is ids of fasta sequences
        #seqlist is list of fasta sequences
        #num_seq is number of fasta sequences
        #seq_length_list is length of each fasta sequence. 
        loa =0 
        count=0
        count_c3=0
        f1=open(os.getcwd()+'/test.log','w+')
        f1.write("%s %s %s\n" % ('#count','number_of_seqs','length_ofalignment'))
        f1.flush()
        #break_tags.txt needs to be deleted manualy each time?
        #f_tag = open('/Users/sridharn/software/consensus_test_repo/temp_files/break_tags.txt','w+')
        print ("-"*30,'WHILE LOOP',"-"*30)
        #f = open(os.getcwd() + '/temp_files/test_graph_values.txt', 'w')
        while True:
            count=count+1
            a=Alignment();h=HMM()
            print('*'*30,"Iteration Number: " + str(count) + '*'*30)
            name_list,sequences,number_of_sequences=a.family_to_string(write_file)
            seq_length_list=a.sequence_length_dist(sequences)
            a1=[]
            for i in sequences:
                a1+=[str(''.join(i))]
            sequences=a1
            length_of_alignment=seq_length_list[0]
            print ("Number of sequences=",number_of_sequences)
            print ("Length of current alignment=",length_of_alignment)
            print ("Length of previous alignment=",loa)
            f1.write(str(count) + ' ' + str(number_of_sequences) + ' ' + str(length_of_alignment) + '\n')
            #Check for break conditions.
            c3,breaks=self.check_break_conditions(number_of_sequences,length_of_alignment,loa,mode,count)
            if c3:
                count_c3=count_c3+1
                print ('***',count_c3,'***')
            if True in breaks or count_c3>=3:
              print ("*"*30,"End of while loop at iteration", count,"*"*30)
              f1.write(str(count_c3)+ ' '+str(count)+' '+str(list(breaks)))
              print (breaks,count_c3)
              #copy file to refined file
              self.copy_file(write_file,refined_file)
              #save consensus
              #cs=''
              if option==1:
                  #cs = self.shuffle_consensus(cs)
                  cs=self.consensus_without_dashes_realign(cs,refined_file,consensus_temp,consensus_aln_temp)

              a.write_fasta(['>>consensus-from-refined-alignment'],[cs],final_consensus_file)
              #print(">>shuffled-consensus\n" + cs)
              #construct profile hmm from msa.(Is all this needed inside the while loop???)
              #output is profile_hmm_file
              h.hmmbuild(profile_hmm_file,refined_file)
              h.emit_n_sequences(number_of_sequences,length_of_alignment,profile_hmm_file,hmm_emitted_file)              
              #align hmm sequences with refined file to generate hmm sequences.
              a.realign(refined_file,hmm_emitted_file,combined_alignment_file)
              a.split_combined_alignment(combined_alignment_file, hmm_emitted_file_aligned)
              #d.call_matlab(refined_file, hmm_emitted_file_aligned, accession)
              #find hmm consensus
              hmm_name_list,hmm_seqs,hmm_nos=a.family_to_string(hmm_emitted_file_aligned)
              a1=[]
              for i in hmm_seqs:
                  a1+=[str(''.join(i))]
              hmm_seqs=a1
              hmm_pm=self.profile_matrix(hmm_seqs)
              hmm_cs=self.find_consensus_sequence(hmm_seqs,hmm_pm,option)
              if option==1:
                  #hmm_cs = self.shuffle_consensus(hmm_cs)
                  hmm_cs=self.consensus_without_dashes_realign(hmm_cs,refined_file,consensus_temp,consensus_aln_temp)
              a.write_fasta(['>>consensus-from-hmm-sequences'],[hmm_cs],hmm_consensus_file)
              #ßf.close()
              f1.close()
              break
            pm = self.profile_matrix(sequences)
            cs = self.find_consensus_sequence(sequences,pm,option) 
            print (cs)
            print ("Consensus sequence length=",len(cs),"\n")
            #Reproduces from consensus.py correctly this far.
            bad_sequence_numbers = self.find_bad_sequences(pm, sequences, name_list)
            sequences, name_list = self.remove_bad_sequences(sequences, name_list, bad_sequence_numbers)
            seq_list=self.sequencestr_to_seq_list(sequences)
            #Remove_dashes from sequence list
            seq_list,num_seq=a.remove_dashes_list(seq_list)
            assert(len(name_list)==len(seq_list))
            a.write_fasta(name_list,seq_list,out_file)
            print ("After removing bad sequences",num_seq,"sequences remain.")
            #Align
            a.fasta_to_mafft(out_file,write_file)
            loa=length_of_alignment
            #old file I/O:sequences->temp_file->out_file->write_file.
            #new file I/O:seq_list->seq_list->out_file->write_file.

class HMM(object):
    '''
    All HMM commands here.
    '''
    def __init__(self):
        return
    def hmmbuild(self,hmmfile_out,msafile):
        #hmmbuild [options] hmmfile alignfile (hmmfile is out, alignfile is in.)
        print ('>>HMM:call_hmmbuild')
        f=open(hmmfile_out,'w+')
        p=Popen(['hmmbuild',hmmfile_out,msafile],stdout=PIPE,stderr=PIPE)
        stdout, stderr = p.communicate()
        p.wait()
        f.close()
        return stdout
    def emit_n_sequences(self,number_of_sequences,length_of_alignment,profile_hmm_file,hmm_emitted_file):
        print (">>HMM:emit_n_sequences")
        #ßcwd = 'hmmemit -N ' + str(N) + ' -o ' + hmm_emitted_sequences + '-L' + str(L) + ' ' + profile_hmm #emit sequences from prpofile hmm

        #Worth initialising filenames as instances global to the entire class?
        N=str(number_of_sequences);L=str(length_of_alignment)
        #profile_hmm_file=profile_hmm_file+'_'+N
        #cwd='hmmemit -N '+N+hmm_emitted_file+' -L '+L+' -p '+profile_hmm_file+' -seed 10001'
        cwd = 'hmmemit -N ' + N + ' -o ' + hmm_emitted_file + ' ' + profile_hmm_file 
        print(cwd)
        #print(N,L, "$"*10)
        p=Popen(cwd,shell=True,stdout=PIPE,stderr=PIPE)
        stdout,stderr=p.communicate(); p.wait()
        return
class DCA(object):
    def __init__(self):
        path=os.getcwd()+'/'
        self.cwd=path
    
    def call_matlab(self, refined_file, hmm_emitted_file_aligned, accession):
        #Call calculate_dca_scores(fasta_train,fasta_test,accession,home)
        #dca scores for refined_file and hmm_emitted_file_aligned
        os.chdir('/usr/local/MATLAB/R2016a/bin') #don't do this! bad practice ! figure out how to use matlab directly from execlist 
        print(">>DCA:call_matlab to do DCA calculations")
        cmd = './matlab -softwareopengl -nodesktop -r ' + '"cd('+"'"+self.cwd+'/martin_dca'+"'" + '); '+'calculate_dca_scores('+"'"+refined_file+"','"
        cmd += hmm_emitted_file_aligned+"','"+accession+"','"+self.cwd+"');"+'exit"'
        process = Popen(cmd,shell=True)
        process.wait()

def main():
    #All this goes into protocol.py 
    #Add argparse arguments for options.
    import argparse
    parser = argparse.ArgumentParser(description="Give it a name YO!!")
    parser.add_argument("--fid","-fid",help="Family ID. e.g.PF04398")
    parser.add_argument("--fidlist","-fidlist", help="File containing list of family IDs. e.g. accession_list.txt")
    parser.add_argument("--con","-con", help="Generate consensus only. Options for different methods?")
    parser.add_argument("--hmm","-hmm",help="Generate profile hmm and emmit hmm sequences.Args:N,L.")
    parser.add_argument("--strategy","-strategy",help="1.for consensus without dashes and with realignment 2.for consensus with dashes") 
    args = parser.parse_args()
    #Initialize classes.
    ch=Check_files();a=Alignment();con=Consensus();home=os.getcwd();dca=DCA()
    #Read list ofs sequences from file.
    ###############
    if args.fid:
        accession=str(args.fid)
        ch.file_exists(home+'/families/'+accession+'.fasta')
        accession_list=[str(accession)]

    elif args.fidlist:
        f1=str(args.fidlist)#list of files containing family IDs (accession_list.txt)
        ch.file_exists(f1)
        accession_list=(open(f1,'r').read().split('\n')[:-1])
        accession=accession_list[0] #??Loop over this in final code for all families??.
        print (accession)


    assert args.strategy, 'Provide consensus design strategy with --strategy'
    option=int(args.strategy)
   ############## 
    #Check all executables/dependencies exist:
    #ch.execs_exist()
    for accession in accession_list:
        ch.file_exists(home+'/families/'+accession+'.fasta')
        fam_file=home+'/families/'+accession+'.fasta'
        mafft_out=home+'/temp_files/test_mafft.fasta'
        #Following ugly_strings. Ugly_strings are very ugly.
        out_file=home+'/temp_files/test_output.fasta'
        write_file=home+'/temp_files/test_write.fasta'
        temp_file=home+'/temp_files/test_temp.fasta'
        consensus_temp=home+'/temp_files/consensus_temp.fasta'
        consensus_aln_temp=home+'/temp_files/consensus_aln_temp.fasta'
        #Read family file 
        idlist,seqlist,num_seq=a.family_to_string(fam_file)
        assert (len(idlist)==len(seqlist))
        assert (num_seq>=500),'Error: Less than 500 sequences in family'
        #Remove dashes
        wod,num_seq=a.remove_dashes_list(seqlist)
        #cdhit cluster
        a.write_fasta(idlist,wod,write_file)
        a.cdhit(write_file,out_file)
        cd_idlist,cd_seqlist,cd_num_seq=a.family_to_string(out_file)
        print ("After clustering with CD-HIT, alignments reduced to",cd_num_seq,"from",num_seq)
        assert (cd_num_seq>=500),'Error: Less that 500 sequences after clustering with CD-HIT'
        #Plot length distribution
        seq_length_list=a.sequence_length_dist(cd_seqlist)   
        #a.plot_length_dist(seq_length_list,home+'length_distributions/'+'PF04398_test')    
        #Get_mode.
        mode= a.mode_of_list(seq_length_list)
        #Zeroeth alignmenst
        stdout,stderr=a.fasta_to_mafft(out_file,write_file)
        mafft_idlist,mafft_seqlist,mafft_num_seq=a.family_to_string(write_file)
        mafft_seq_length_list=a.sequence_length_dist(write_file)
        #Now iterate.
        # Define where to put output files.
        refined_file= home+'/refined_alignments/'+accession+'_refined.fasta'
        final_consensus_file=home+'/refined_consensuses/'+accession +'_refined_consensus.fasta'
        profile_hmm_file=home+'/hmm_profiles/'+accession+'_profile.hmm'
        hmm_emitted_file=home+'/hmm_emitted_sequences/'+accession+'_hmm_emitted_sequences.fasta'
        combined_alignment_file=home+'/combined_alignments/'+accession+'_combined.fasta'
        hmm_emitted_file_aligned=home+'/hmm_emitted_sequences_aligned/'+accession+'_hmmsequences_aligned.fasta'
        hmm_consensus_file=home+'/hmm_consensuses/'+accession+'_hmm_consensus.fasta'
        #Get consensus through iterative msa alignment with mafft and generate hmm sequences as well.
        con.iterate(mode,mafft_idlist,mafft_seqlist,mafft_num_seq,mafft_seq_length_list,write_file,refined_file,temp_file,out_file,final_consensus_file,
                profile_hmm_file,hmm_emitted_file,combined_alignment_file, hmm_emitted_file_aligned,consensus_temp,consensus_aln_temp,option,hmm_consensus_file)    
    #Call DCA
        dca.call_matlab(refined_file,hmm_emitted_file_aligned,accession)
        con.copy_file('test.log',accession+'_'+str(option)+'.log')
main()
