import FWCore.ParameterSet.Config as cms
import glob

process = cms.Process("qgMiniTupleProducer")

# Settings for local tests
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(10000))

isData=False

#######################################
###              GT                 ###
#######################################
# used by photon id and jets
process.load("Configuration.Geometry.GeometryIdeal_cff") 
process.load('Configuration.StandardSequences.Services_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")

#mc https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions#Global_Tags_for_Run2_MC_Producti
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
if (isData):
        process.GlobalTag.globaltag = '76X_dataRun2_16Dec2015_v0'
else:
        process.GlobalTag.globaltag = '76X_mcRun2_asymptotic_RunIIFall15DR76_v1'
############## END GT #################

#######################################
###            Input                ###
#######################################
fileList=['/store/mc/RunIIFall15MiniAODv2/QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/00000/04348357-EDB8-E511-BDA4-008CFA197D2C.root']

### do not remove the line below!
###FILELIST###

process.source = cms.Source("PoolSource", 
   fileNames=cms.untracked.vstring(fileList)
)

#######################################
###            Output               ###
#######################################
# Use TFileService to put trees from different analyzers in one file
process.TFileService = cms.Service("TFileService", 
    fileName = cms.string("qgMiniTuple.root"),
    closeFileFast = cms.untracked.bool(True)
)
#######################################
###             JEC                 ###
#######################################

from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection

jecLevels= ['L1FastJet',  'L2Relative', 'L3Absolute']
if isData:
	jecLevels.append( 'L2L3Residuals')

updateJetCollection(
   process,
   jetSource = cms.InputTag('slimmedJets'),
   labelName = 'UpdatedJEC',
   jetCorrections = ('AK4PFchs', cms.vstring(jecLevels), 'None')  # Do not forget 'L2L3Residual' on data!
)
print "-> Updating the jets collection to run on to 'updatedPatJetsUpdatedJEC' with the new jec in the GT"
process.jecSequence = cms.Sequence( process.patJetCorrFactorsUpdatedJEC* process.updatedPatJetsUpdatedJEC )
############### END JEC ###############

#######################################
###            Config               ###
#######################################
process.qgMiniTupleAK4chs = cms.EDAnalyzer("qgMiniTuple",
    rhoInputTag			= cms.InputTag('fixedGridRhoFastjetAll'),
    csvInputTag			= cms.InputTag('pfCombinedInclusiveSecondaryVertexV2BJetTags'),
    vertexInputTag		= cms.InputTag('offlineSlimmedPrimaryVertices'),
    jetsInputTag		= cms.InputTag('updatedPatJetsUpdatedJEC'),
    genJetsInputTag		= cms.InputTag('slimmedGenJets'),
    genParticlesInputTag	= cms.InputTag('prunedGenParticles'),
    pfCandidatesInputTag	= cms.InputTag('packedPFCandidates'),
    minJetPt			= cms.untracked.double(20.),
    deltaRcut			= cms.untracked.double(0.3),
    jec				= cms.string(''),						# Ignored when using pat mode
)


#######################################
###              Path               ###
#######################################

process.p = cms.Path(process.jecSequence * process.qgMiniTupleAK4chs)

