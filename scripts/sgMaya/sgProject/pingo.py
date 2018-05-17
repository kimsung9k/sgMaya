from maya import cmds
import pymel.core
from sgMaya import sgCmds
from sgMaya.sgCmds import setTransformDefault


def retargetPoint( target, targetBase, ctl, ctlBase ):
    
    multMtx  = pymel.core.createNode( 'multMatrix' )
    target.wm >> multMtx.i[0]
    targetBase.wim >> multMtx.i[1]
    ctlBase.wm >> multMtx.i[2]
    ctl.pim >> multMtx.i[3]
    dcmp = pymel.core.createNode( 'decomposeMatrix' )
    multMtx.matrixSum >> dcmp.imat
    ctlP = ctl.getParent()
    realPointer = pymel.core.createNode( 'transform' )
    realPointer.setParent( ctlP ); realPointer.r.set( 0,0,0 ); realPointer.s.set( 1,1,1 )
    dcmp.ot >> realPointer.t
    pymel.core.pointConstraint( realPointer, ctl )



def retargetParent( target, targetBase, ctl, ctlBase ):
    
    multMtx  = pymel.core.createNode( 'multMatrix' )
    target.wm >> multMtx.i[0]
    targetBase.wim >> multMtx.i[1]
    ctlBase.wm >> multMtx.i[2]
    ctl.pim >> multMtx.i[3]
    dcmp = pymel.core.createNode( 'decomposeMatrix' )
    multMtx.matrixSum >> dcmp.imat
    ctlP = ctl.getParent()
    realPointer = pymel.core.createNode( 'transform' )
    realPointer.setParent( ctlP ); realPointer.r.set( 0,0,0 ); realPointer.s.set( 1,1,1 )
    dcmp.ot >> realPointer.t
    pymel.core.pointConstraint( realPointer, ctl )
    dcmp.outputRotate >> ctl.r



def retargetRotate( target, targetBase, ctl, ctlBase ):
    
    multMtx  = pymel.core.createNode( 'multMatrix' )
    target.wm >> multMtx.i[0]
    targetBase.wim >> multMtx.i[1]
    ctlBase.wm >> multMtx.i[2]
    ctl.pim >> multMtx.i[3]
    dcmp = pymel.core.createNode( 'decomposeMatrix' )
    multMtx.matrixSum >> dcmp.imat
    dcmp.outputRotate >> ctl.r



def setLocatorForAram( mocGrp, grpName = 'MOCJNT_grp' ):
    
    if grpName:
        ns = mocGrp.replace( grpName, '' )
    else:
        ns = ':'.join( mocGrp.split( ':' )[:-1] )
    sgCmds.createRetargetLocator( mocGrp )

    MOCJNT_ballEnd_L_ = pymel.core.ls( ns + 'MOCJNT_ballEnd_L_' )[0]
    MOCJNT_ankle_L__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_ankle_L__rtLock_offset' )[0]
    
    MOCJNT_ballEnd_R_ = pymel.core.ls( ns + 'MOCJNT_ballEnd_R_' )[0]
    MOCJNT_ankle_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_ankle_R__rtLock_offset' )[0]
    
    MOCJNT_ankle_L__rtLock_offset.setParent( MOCJNT_ballEnd_L_ )
    MOCJNT_ankle_R__rtLock_offset.setParent( MOCJNT_ballEnd_R_ )
    
    sgCmds.setRotateDefault( MOCJNT_ankle_L__rtLock_offset )
    sgCmds.setRotateDefault( MOCJNT_ankle_R__rtLock_offset )
    
    MOCJNT_ankle_R__rtLock_offset.attr( 'rotateZ' ).set( 180 )
    
    MOCJNT_hip_L_  = pymel.core.ls( ns + 'MOCJNT_hip_L_' )[0]
    MOCJNT_knee_L_ = pymel.core.ls( ns + 'MOCJNT_knee_L_' )[0]
    MOCJNT_knee_L__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_knee_L__rtLock_offset' )[0]
    MOCJNT_knee_L__rtLock = pymel.core.ls( ns + 'MOCJNT_knee_L__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_hip_L_, MOCJNT_knee_L_, MOCJNT_knee_L__rtLock_offset, ct=0, cr=1, cs=0 )
    MOCJNT_knee_L__rtLock.ty.set( 2 )
    MOCJNT_knee_L__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    MOCJNT_hip_R_  = pymel.core.ls( ns + 'MOCJNT_hip_R_' )[0]; pymel.core.select( MOCJNT_hip_R_ )
    MOCJNT_hip_R_c = pymel.core.joint( n=ns+'MOCJNT_hip_R_c' ); MOCJNT_hip_R_c.r.set( 180, 0, -180 )
    MOCJNT_knee_R_ = pymel.core.ls( ns + 'MOCJNT_knee_R_' )[0]
    MOCJNT_knee_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_knee_R__rtLock_offset' )[0]
    MOCJNT_knee_R__rtLock = pymel.core.ls( ns + 'MOCJNT_knee_R__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_hip_R_c, MOCJNT_knee_R_, MOCJNT_knee_R__rtLock_offset, ct=0, cr=1 )
    MOCJNT_knee_R__rtLock.ty.set( -2 )
    MOCJNT_knee_R__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    
    MOCJNT_shoulder_L_  = pymel.core.ls( ns + 'MOCJNT_shoulder_L_' )[0]
    MOCJNT_elbow_L_ = pymel.core.ls( ns + 'MOCJNT_elbow_L_' )[0]
    MOCJNT_elbow_L__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_elbow_L__rtLock_offset' )[0]
    MOCJNT_elbow_L__rtLock = pymel.core.ls( ns + 'MOCJNT_elbow_L__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_shoulder_L_, MOCJNT_elbow_L_, MOCJNT_elbow_L__rtLock_offset, ct=0, cr=1 )
    MOCJNT_elbow_L__rtLock.tz.set( -2 )
    MOCJNT_elbow_L__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    MOCJNT_shoulder_R_  = pymel.core.ls( ns + 'MOCJNT_shoulder_R_' )[0]; pymel.core.select( MOCJNT_shoulder_R_ )
    MOCJNT_shoulder_R_c = pymel.core.joint( n=ns+'MOCJNT_shoulder_R_c' ); MOCJNT_shoulder_R_c.r.set( 180, 0, -180 )
    MOCJNT_elbow_R_ = pymel.core.ls( ns + 'MOCJNT_elbow_R_' )[0]
    MOCJNT_elbow_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_elbow_R__rtLock_offset' )[0]
    MOCJNT_elbow_R__rtLock = pymel.core.ls( ns + 'MOCJNT_elbow_R__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_shoulder_R_c, MOCJNT_elbow_R_, MOCJNT_elbow_R__rtLock_offset, ct=0, cr=1, cs=0 )
    MOCJNT_elbow_R__rtLock.tz.set( 2 )
    MOCJNT_elbow_R__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    MOCJNT_chest_rtLock_offset = pymel.core.ls( ns + 'MOCJNT_chest_rtLock_offset' )[0]
    MOCJNT_chest_rtLock_offset.r.set( 180, 90, 90 )
    
    MOCJNT_head_rtLock = pymel.core.ls( ns + 'MOCJNT_head_rtLock' )[0]
    MOCJNT_head_rtLock.r.set( 180, 90, 90 )
    
    MOCJNT_wrist_R__rtLock = pymel.core.ls( ns + 'MOCJNT_wrist_R__rtLock' )[0]
    MOCJNT_wrist_R__rtLock.r.set( 180, 0, 0 )
    
    MOCJNT_wrist_R__rtLock2 = pymel.core.spaceLocator( n=ns + 'MOCJNT_wrist_R__rtLock2' )
    MOCJNT_wrist_R_ = pymel.core.ls( ns + 'MOCJNT_wrist_R_' )[0]
    MOCJNT_wrist_R__rtLock2.setParent( MOCJNT_wrist_R_ )
    sgCmds.setTransformDefault( MOCJNT_wrist_R__rtLock2 )
    
    MOCJNT_shoulder_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_shoulder_R__rtLock_offset' )[0]
    MOCJNT_shoulder_R__rtLock_offset.r.set( 180, 0, -180 )

    MOCJNT_hip_R__rtLock = pymel.core.ls( ns + 'MOCJNT_hip_R__rtLock' )[0]
    MOCJNT_hip_R__rtLock.r.set( 0, 180, 0 )
    
    MOCJNT_knee_L_ = pymel.core.ls( ns + 'MOCJNT_knee_L_' )[0]
    MOCJNT_knee_L__rtLock2 = pymel.core.spaceLocator( n='MOCJNT_knee_L__rtLock2' )
    MOCJNT_knee_L__rtLock2.setParent( MOCJNT_knee_L_ )
    
    MOCJNT_knee_R_ = pymel.core.ls( ns + 'MOCJNT_knee_R_' )[0]
    MOCJNT_knee_R__rtLock2 = pymel.core.spaceLocator( n='MOCJNT_knee_R__rtLock2' )
    MOCJNT_knee_R__rtLock2.setParent( MOCJNT_knee_R_ )
    
    MOCJNT_elbow_L__rtLock2 = pymel.core.spaceLocator(n= ns + 'MOCJNT_elbow_L__rtLock2')
    MOCJNT_elbow_L__rtLock2.setParent( MOCJNT_elbow_L_ )
    sgCmds.setTransformDefault( MOCJNT_elbow_L__rtLock2 )
    
    MOCJNT_elbow_R__rtLock2 = pymel.core.spaceLocator(n= ns + 'MOCJNT_elbow_R__rtLock2')
    MOCJNT_elbow_R__rtLock2.setParent( MOCJNT_elbow_R_ )
    sgCmds.setTransformDefault( MOCJNT_elbow_R__rtLock2 )
    
    


def connectMocForAram( mocGrp, rigGrp, mocGrpName='MOCJNT_grp', aramGrpName='ARAM_Set' ):
    
    if mocGrpName:
        mocns = mocGrp.replace( mocGrpName, '' )
    else:
        mocns = ':'.join( mocGrp.split( ':' )[:-1] )
    
    if aramGrpName:
        rigns = rigGrp.replace( aramGrpName, '' )
    else:
        rigns = ':'.join( rigGrp.split( ':' )[:-1] )
    
    setLocatorForAram( mocGrp, mocGrpName )
    
    ARAM_MainC    = pymel.core.ls( rigns + 'ARAM_MainC' )[0]
    MOCJNT_grp = pymel.core.ls( mocns + 'MOCJNT_grp' )[0]
    
    retargetParentSrcList = ['MOCJNT_root_rtLock', 'MOCJNT_ankle_L__rtLock', 'MOCJNT_ankle_R__rtLock', 'MOCJNT_wrist_L__rtLock', 'MOCJNT_wrist_R__rtLock']
    retargetParentTrgList = ['ARAM_ROOTC', 'ARAM_lFootIKC', 'ARAM_rFootIKC', 'ARAM_lWristIKC', 'ARAM_rWristIKC']
    
    for i in range( len( retargetParentSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetParentSrcList[i] )[0]
        CTL = pymel.core.ls( rigns + retargetParentTrgList[i] )[0]
        retargetParent( MOCJNT, MOCJNT_grp, CTL, ARAM_MainC )
    
    
    retargetRotateSrcList = ['MOCJNT_spines_0_rtLock', 'MOCJNT_spines_1_rtLock', 'MOCJNT_chest_rtLock', 'MOCJNT_head_rtLock', 
                             'MOCJNT_clevicle_L__rtLock', 'MOCJNT_clevicle_R__rtLock', 'MOCJNT_shoulder_L__rtLock', 'MOCJNT_shoulder_R__rtLock',
                             'MOCJNT_hip_L__rtLock', 'MOCJNT_hip_R__rtLock']
    retargetRotateTrgList = ['ARAM_Spine01FKC', 'ARAM_Spine02FKC', 'ARAM_SpineTopIKC', 'ARAM_HeadC', 
                             'ARAM_lClavicleC', 'ARAM_rClavicleC', 'ARAM_lShoulderFKC', 'ARAM_rShoulderFKC',
                             'ARAM_lHipFKC', 'ARAM_rHipFKC']
    
    for i in range( len( retargetRotateSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetRotateSrcList[i] )[0]
        CTL = pymel.core.ls( rigns + retargetRotateTrgList[i] )[0]
        retargetRotate( MOCJNT, MOCJNT_grp, CTL, ARAM_MainC )


    retargetPointSrcList = ['MOCJNT_elbow_L__rtLock', 'MOCJNT_elbow_R__rtLock', 'MOCJNT_knee_L__rtLock', 'MOCJNT_knee_R__rtLock']
    retargetPointTrgList = ['ARAM_lElbowIKC', 'ARAM_rElbowIKC', 'ARAM_lKneeIKC', 'ARAM_rKneeIKC']
    
    for i in range( len( retargetPointSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetPointSrcList[i] )[0]
        CTL = pymel.core.ls( rigns + retargetPointTrgList[i] )[0]
        retargetPoint( MOCJNT, MOCJNT_grp, CTL, ARAM_MainC )
    pymel.core.ls( rigns + 'ARAM_lFootIKC' )[0].attr( 'rotateOrder' ).set( 0 )
    pymel.core.ls( rigns + 'ARAM_rFootIKC' )[0].attr( 'rotateOrder' ).set( 0 )


    MOCJNT_ball_L_rz = pymel.core.ls( mocns + 'MOCJNT_ball_L_.rz' )[0]
    MOCJNT_ball_R_rz = pymel.core.ls( mocns + 'MOCJNT_ball_R_.rz' )[0]
    ARAM_lFootIKC_heelBall = pymel.core.ls( rigns + 'ARAM_lFootIKC.heelBall' )[0]
    ARAM_rFootIKC_heelBall = pymel.core.ls( rigns + 'ARAM_rFootIKC.heelBall' )[0]
    
    multNode_forBall_L_ = pymel.core.createNode( 'multDoubleLinear' ); multNode_forBall_L_.input2.set( 0.1111 )
    multNode_forBall_R_ = pymel.core.createNode( 'multDoubleLinear' ); multNode_forBall_R_.input2.set( 0.1111 )
    MOCJNT_ball_L_rz >> multNode_forBall_L_.input1
    MOCJNT_ball_R_rz >> multNode_forBall_R_.input1
    
    multNode_forBall_L_.output >> ARAM_lFootIKC_heelBall
    multNode_forBall_R_.output >> ARAM_rFootIKC_heelBall
    
    mocloc_L_list = ['MOCJNT_wrist_L__rtLock', 'MOCJNT_elbow_L__rtLock2','MOCJNT_shoulder_L__rtLock']
    ctl_L_list = [ 'ARAM_lWristFKC', 'ARAM_lElbowFKC', 'ARAM_lShoulderFKC' ]
    
    for i in range( len( mocloc_L_list )-1 ):
        MOCJNT = pymel.core.ls( mocns + mocloc_L_list[i] )[0]
        MOCJNT_P = pymel.core.ls( mocns + mocloc_L_list[i+1] )[0]
        CTL = pymel.core.ls( rigns + ctl_L_list[i] )[0]
        CTL_P = pymel.core.ls( rigns + ctl_L_list[i+1] )[0]
        retargetRotate( MOCJNT, MOCJNT_P, CTL, CTL_P )
    
    
    mocloc_R_list = ['MOCJNT_wrist_R__rtLock2', 'MOCJNT_elbow_R__rtLock2','MOCJNT_shoulder_R__rtLock']
    ctl_R_list = [ 'ARAM_rWristFKC', 'ARAM_rElbowFKC', 'ARAM_rShoulderFKC' ]
    
    for i in range( len( mocloc_L_list )-1 ):
        MOCJNT = pymel.core.ls( mocns + mocloc_R_list[i] )[0]
        MOCJNT_P = pymel.core.ls( mocns + mocloc_R_list[i+1] )[0]
        CTL = pymel.core.ls( rigns + ctl_R_list[i] )[0]
        CTL_P = pymel.core.ls( rigns + ctl_R_list[i+1] )[0]
        retargetRotate( MOCJNT, MOCJNT_P, CTL, CTL_P )
    
    
    


def setLocatorForPipi( mocGrp, grpName = 'MOCJNT_grp' ):
    
    if grpName:
        ns = mocGrp.replace( grpName, '' )
    else:
        ns = ':'.join( mocGrp.split( ':' )[:-1] )
    sgCmds.createRetargetLocator( mocGrp )

    MOCJNT_ballEnd_L_ = pymel.core.ls( ns + 'MOCJNT_ballEnd_L_' )[0]
    MOCJNT_ankle_L__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_ankle_L__rtLock_offset' )[0]
    
    MOCJNT_ballEnd_R_ = pymel.core.ls( ns + 'MOCJNT_ballEnd_R_' )[0]
    MOCJNT_ankle_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_ankle_R__rtLock_offset' )[0]
    
    MOCJNT_ankle_L__rtLock_offset.setParent( MOCJNT_ballEnd_L_ )
    MOCJNT_ankle_R__rtLock_offset.setParent( MOCJNT_ballEnd_R_ )
    
    sgCmds.setRotateDefault( MOCJNT_ankle_L__rtLock_offset )
    sgCmds.setRotateDefault( MOCJNT_ankle_R__rtLock_offset )
    
    MOCJNT_ankle_R__rtLock_offset.attr( 'rotateZ' ).set( 180 )
    
    MOCJNT_hip_L_  = pymel.core.ls( ns + 'MOCJNT_hip_L_' )[0]
    MOCJNT_knee_L_ = pymel.core.ls( ns + 'MOCJNT_knee_L_' )[0]
    MOCJNT_knee_L__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_knee_L__rtLock_offset' )[0]
    MOCJNT_knee_L__rtLock = pymel.core.ls( ns + 'MOCJNT_knee_L__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_hip_L_, MOCJNT_knee_L_, MOCJNT_knee_L__rtLock_offset, ct=0, cr=1, cs=0 )
    MOCJNT_knee_L__rtLock.ty.set( 2 )
    MOCJNT_knee_L__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    MOCJNT_hip_R_  = pymel.core.ls( ns + 'MOCJNT_hip_R_' )[0]; pymel.core.select( MOCJNT_hip_R_ )
    MOCJNT_hip_R_c = pymel.core.joint( n=ns+'MOCJNT_hip_R_c' ); MOCJNT_hip_R_c.r.set( 180, 0, -180 )
    MOCJNT_knee_R_ = pymel.core.ls( ns + 'MOCJNT_knee_R_' )[0]
    MOCJNT_knee_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_knee_R__rtLock_offset' )[0]
    MOCJNT_knee_R__rtLock = pymel.core.ls( ns + 'MOCJNT_knee_R__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_hip_R_c, MOCJNT_knee_R_, MOCJNT_knee_R__rtLock_offset, ct=0, cr=1 )
    MOCJNT_knee_R__rtLock.ty.set( -2 )
    MOCJNT_knee_R__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    
    MOCJNT_shoulder_L_  = pymel.core.ls( ns + 'MOCJNT_shoulder_L_' )[0]
    MOCJNT_elbow_L_ = pymel.core.ls( ns + 'MOCJNT_elbow_L_' )[0]
    MOCJNT_elbow_L__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_elbow_L__rtLock_offset' )[0]
    MOCJNT_elbow_L__rtLock = pymel.core.ls( ns + 'MOCJNT_elbow_L__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_shoulder_L_, MOCJNT_elbow_L_, MOCJNT_elbow_L__rtLock_offset, ct=0, cr=1 )
    MOCJNT_elbow_L__rtLock.tz.set( -2 )
    MOCJNT_elbow_L__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    MOCJNT_shoulder_R_  = pymel.core.ls( ns + 'MOCJNT_shoulder_R_' )[0]; pymel.core.select( MOCJNT_shoulder_R_ )
    MOCJNT_shoulder_R_c = pymel.core.joint( n=ns+'MOCJNT_shoulder_R_c' ); MOCJNT_shoulder_R_c.r.set( 180, 0, -180 )
    MOCJNT_elbow_R_ = pymel.core.ls( ns + 'MOCJNT_elbow_R_' )[0]
    MOCJNT_elbow_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_elbow_R__rtLock_offset' )[0]
    MOCJNT_elbow_R__rtLock = pymel.core.ls( ns + 'MOCJNT_elbow_R__rtLock' )[0]
    
    sgCmds.blendTwoMatrixConnect( MOCJNT_shoulder_R_c, MOCJNT_elbow_R_, MOCJNT_elbow_R__rtLock_offset, ct=0, cr=1, cs=0 )
    MOCJNT_elbow_R__rtLock.tz.set( 2 )
    MOCJNT_elbow_R__rtLock.getShape().attr( 'localScale' ).set( 0.3,0.3,0.3 )
    
    MOCJNT_chest_rtLock_offset = pymel.core.ls( ns + 'MOCJNT_chest_rtLock_offset' )[0]
    MOCJNT_chest_rtLock_offset.r.set( 180, 90, 90 )
    
    MOCJNT_head_rtLock = pymel.core.ls( ns + 'MOCJNT_head_rtLock' )[0]
    MOCJNT_head_rtLock.r.set( 180, 90, 90 )
    
    MOCJNT_wrist_R__rtLock = pymel.core.ls( ns + 'MOCJNT_wrist_R__rtLock' )[0]
    MOCJNT_wrist_R__rtLock.r.set( 180, 0, 0 )
    
    MOCJNT_shoulder_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_shoulder_R__rtLock_offset' )[0]
    MOCJNT_shoulder_R__rtLock_offset.r.set( 180, 0, -180 )
    
    MOCJNT_clevicle_L__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_clevicle_L__rtLock_offset' )[0]
    MOCJNT_clevicle_L__rtLock_offset.r.set( 180, 0, 0 )
    MOCJNT_clevicle_R__rtLock_offset = pymel.core.ls( ns + 'MOCJNT_clevicle_R__rtLock_offset' )[0]
    MOCJNT_clevicle_R__rtLock_offset.r.set( 180, 0, 0 )



    MOCJNT_shoulder_L__rtLock2 = pymel.core.spaceLocator( n = ns + 'MOCJNT_shoulder_L__rtLock2' )
    MOCJNT_shoulder_L__rtLock2.setParent( MOCJNT_shoulder_L_ )
    sgCmds.setAllDefault( MOCJNT_shoulder_L__rtLock2 ); MOCJNT_shoulder_L__rtLock2.rx.set( 180 )
    
    MOCJNT_elbow_L__rtLock2 = pymel.core.spaceLocator( n = ns + 'MOCJNT_elbow_L__rtLock2' )
    MOCJNT_elbow_L__rtLock2.setParent( MOCJNT_elbow_L_ )
    sgCmds.setAllDefault( MOCJNT_elbow_L__rtLock2 ); MOCJNT_elbow_L__rtLock2.rx.set( 180 )
    
    MOCJNT_wrist_L_ = pymel.core.ls( ns + 'MOCJNT_wrist_L_' )[0]
    MOCJNT_wrist_L__rtLock2 = pymel.core.spaceLocator( n = ns + 'MOCJNT_wrist_L__rtLock2' )
    MOCJNT_wrist_L__rtLock2.setParent( MOCJNT_wrist_L_ )
    sgCmds.setAllDefault( MOCJNT_wrist_L__rtLock2 ); MOCJNT_wrist_L__rtLock2.rx.set( 180 )
    
    
    MOCJNT_shoulder_R__rtLock2 = pymel.core.spaceLocator( n = ns + 'MOCJNT_shoulder_R__rtLock2' )
    MOCJNT_shoulder_R__rtLock2.setParent( MOCJNT_shoulder_R_ )
    sgCmds.setAllDefault( MOCJNT_shoulder_R__rtLock2 ); MOCJNT_shoulder_R__rtLock2.r.set( 180, 0, 180 )
    
    MOCJNT_elbow_R__rtLock2 = pymel.core.spaceLocator( n = ns + 'MOCJNT_elbow_R__rtLock2' )
    MOCJNT_elbow_R__rtLock2.setParent( MOCJNT_elbow_R_ )
    sgCmds.setAllDefault( MOCJNT_elbow_R__rtLock2 ); MOCJNT_elbow_R__rtLock2.rx.set( 180 )
    
    MOCJNT_wrist_R_ = pymel.core.ls( ns + 'MOCJNT_wrist_R_' )[0]
    MOCJNT_wrist_R__rtLock2 = pymel.core.spaceLocator( n = ns + 'MOCJNT_wrist_R__rtLock2' )
    MOCJNT_wrist_R__rtLock2.setParent( MOCJNT_wrist_R_ )
    sgCmds.setAllDefault( MOCJNT_wrist_R__rtLock2 ); MOCJNT_wrist_R__rtLock2.rx.set( 180 )
    



def connectMocForPipi( mocGrp, rigGrp, mocGrpName='MOCJNT_grp', pipiGrpName='CH_Pipi' ):
    
    if mocGrpName:
        mocns = mocGrp.replace( mocGrpName, '' )
    else:
        mocns = ':'.join( mocGrp.split( ':' )[:-1] )
    
    if pipiGrpName:
        rigns = rigGrp.replace( pipiGrpName, '' )
    else:
        rigns = ':'.join( rigGrp.split( ':' )[:-1] )
    
    setLocatorForPipi( mocGrp, mocGrpName )

    Move_Ctrl    = pymel.core.ls( rigns + 'Move_Ctrl' )[0]
    MOCJNT_grp = pymel.core.ls( mocns + 'MOCJNT_grp' )[0]
    
    
    retargetRotateSrcList = ['MOCJNT_spines_0_rtLock', 'MOCJNT_spines_1_rtLock', 'MOCJNT_chest_rtLock', 'MOCJNT_head_rtLock', 
                             'MOCJNT_clevicle_L__rtLock', 'MOCJNT_clevicle_R__rtLock']
    retargetRotateTrgList = ['SpineFk1_Ctrl', 'SpineFk2_Ctrl', 'Chest_Ctrl', 'Head_Ctrl', 
                             'LfClavicle_Ctrl', 'RtClavicle_Ctrl']
    
    for i in range( len( retargetRotateSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetRotateSrcList[i] )[0]
        CTL = pymel.core.ls( rigns + retargetRotateTrgList[i] )[0]
        retargetRotate( MOCJNT, MOCJNT_grp, CTL, Move_Ctrl )


    retargetPointSrcList = ['MOCJNT_elbow_L__rtLock', 'MOCJNT_elbow_R__rtLock', 'MOCJNT_knee_L__rtLock', 'MOCJNT_knee_R__rtLock']
    retargetPointTrgList = ['LfArmPv_Ctrl', 'RtArmPv_Ctrl','LfLegPv_Ctrl', 'RtLegPv_Ctrl']
    
    for i in range( len( retargetPointSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetPointSrcList[i] )[0]
        CTL = pymel.core.ls( rigns + retargetPointTrgList[i] )[0]
        retargetPoint( MOCJNT, MOCJNT_grp, CTL, Move_Ctrl )

    MOCJNT_ball_L_rz = pymel.core.ls( mocns + 'MOCJNT_ball_L_.rz' )[0]
    MOCJNT_ball_R_rz = pymel.core.ls( mocns + 'MOCJNT_ball_R_.rz' )[0]
    LfLegIk_Ctrl_footRoll = pymel.core.ls( rigns + 'LfLegIk_Ctrl.FootRoll' )[0]
    RtLegIk_Ctrl_footRoll = pymel.core.ls( rigns + 'RtLegIk_Ctrl.FootRoll' )[0]
    
    multNode_forBall_L_ = pymel.core.createNode( 'multDoubleLinear' ); multNode_forBall_L_.input2.set( 0.1111 )
    multNode_forBall_R_ = pymel.core.createNode( 'multDoubleLinear' ); multNode_forBall_R_.input2.set( 0.1111 )
    MOCJNT_ball_L_rz >> multNode_forBall_L_.input1
    MOCJNT_ball_R_rz >> multNode_forBall_R_.input1
    
    multNode_forBall_L_.output >> LfLegIk_Ctrl_footRoll
    multNode_forBall_R_.output >> RtLegIk_Ctrl_footRoll
    
    #---------------------------------------------------------------
    
    retargetParentSrcList = [ 'MOCJNT_root_rtLock', 'MOCJNT_ankle_L__rtLock', 'MOCJNT_ankle_R__rtLock' ]
    retargetParentTrgList = [ 'Root_Ctrl', 'LfLegIk_Ctrl', 'RtLegIk_Ctrl' ]
    
    Move_Ctrl_child = pymel.core.createNode( 'transform', n = Move_Ctrl + '_offset' )
    Move_Ctrl_child.setParent( Move_Ctrl ); Move_Ctrl_child.t.set( 0,0,0); Move_Ctrl_child.r.set( 0,0,0 )
    Move_Ctrl_child.s.set( 1.1, 1, 1.1 )
    
    for i in range( len( retargetParentSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetParentSrcList[i] )[0]
        CTL = pymel.core.ls( rigns + retargetParentTrgList[i] )[0]
        retargetParent( MOCJNT, MOCJNT_grp, CTL, Move_Ctrl_child )
        if i == 0: continue
        CTL.attr( 'PvCtrlVisibility' ).set( 1 )
    
    #---------------------------------------------------------------
    
    def setTransformDefault( inputTarget ):
        target = pymel.core.ls( inputTarget )[0]
        attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        values = [0,0,0,0,0,0,1,1,1]
        for i in range( len( attrs ) ):
            try:cmds.setAttr( target + '.' + attrs[i], values[i] )
            except:pass
    
    retargetShoulder_L_ = pymel.core.createNode( 'transform', n = rigns + 'RootObj_Shoulder_L_' )
    retargetShoulder_R_ = pymel.core.createNode( 'transform', n = rigns + 'RootObj_Shoulder_R_' )
    retargetShoulder_L_.setParent( rigns + 'LfClavicle_Ctrl' ); retargetShoulder_L_.dh.set(1)
    retargetShoulder_R_.setParent( rigns + 'RtClavicle_Ctrl' ); retargetShoulder_R_.dh.set(1)
    setTransformDefault( retargetShoulder_L_ ); retargetShoulder_L_.tx.set( 1.09 )
    setTransformDefault( retargetShoulder_R_ ); retargetShoulder_R_.tx.set( -1.09 )
    retargetShoulder_L_.s.set( 1.54, 1.54, 1.54 )
    retargetShoulder_R_.s.set( 1.54, 1.54, 1.54 )
    
    retargetRotateSrcList = ['MOCJNT_shoulder_L__rtLock', 'MOCJNT_shoulder_R__rtLock']
    retargetRotateTrgList = ['RootObj_Shoulder_L_', 'RootObj_Shoulder_R_' ]
    
    for i in range( len( retargetRotateSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetRotateSrcList[i] )[0]
        CTL = pymel.core.ls( rigns + retargetRotateTrgList[i] )[0]
        retargetRotate( MOCJNT, MOCJNT_grp, CTL, Move_Ctrl )
    
    retargetParentSrcList = [ ['MOCJNT_wrist_L__rtLock','MOCJNT_shoulder_L__rtLock'], ['MOCJNT_wrist_R__rtLock','MOCJNT_shoulder_R__rtLock'] ]
    retargetParentTrgList = [ ['LfArmIk_Ctrl','RootObj_Shoulder_L_'], ['RtArmIk_Ctrl','RootObj_Shoulder_R_'] ]
    
    for i in range( len( retargetParentSrcList ) ):
        MOCJNT = pymel.core.ls( mocns + retargetParentSrcList[i][0] )[0]
        CTL = pymel.core.ls( rigns + retargetParentTrgList[i][0] )[0]
        MOCJNT_base = pymel.core.ls( mocns + retargetParentSrcList[i][1] )[0]
        CTL_base = pymel.core.ls( rigns + retargetParentTrgList[i][1] )[0]
        retargetParent( MOCJNT, MOCJNT_base, CTL, CTL_base )
        CTL.attr( 'PvCtrlVisibility' ).set( 1 )

    
    
    mocloc_L_list = ['MOCJNT_wrist_L__rtLock2', 'MOCJNT_elbow_L__rtLock2','MOCJNT_shoulder_L__rtLock2', 'MOCJNT_clevicle_L__rtLock']
    ctl_L_list = [ 'LfArm3Fk_Ctrl', 'LfArm2Fk_Ctrl', 'LfArm1Fk_Ctrl', 'LfClavicle_Ctrl' ]
    
    for i in range( len( mocloc_L_list )-1 ):
        MOCJNT = pymel.core.ls( mocns + mocloc_L_list[i] )[0]
        MOCJNT_P = pymel.core.ls( mocns + mocloc_L_list[i+1] )[0]
        CTL = pymel.core.ls( rigns + ctl_L_list[i] )[0]
        CTL_P = pymel.core.ls( rigns + ctl_L_list[i+1] )[0]
        retargetRotate( MOCJNT, MOCJNT_P, CTL, CTL_P )
    
    
    mocloc_R_list = ['MOCJNT_wrist_R__rtLock2', 'MOCJNT_elbow_R__rtLock2','MOCJNT_shoulder_R__rtLock2', 'MOCJNT_clevicle_R__rtLock']
    ctl_R_list = [ 'RtArm3Fk_Ctrl', 'RtArm2Fk_Ctrl', 'RtArm1Fk_Ctrl', 'RtClavicle_Ctrl' ]
    
    for i in range( len( mocloc_L_list )-1 ):
        MOCJNT = pymel.core.ls( mocns + mocloc_R_list[i] )[0]
        MOCJNT_P = pymel.core.ls( mocns + mocloc_R_list[i+1] )[0]
        CTL = pymel.core.ls( rigns + ctl_R_list[i] )[0]
        CTL_P = pymel.core.ls( rigns + ctl_R_list[i+1] )[0]
        retargetRotate( MOCJNT, MOCJNT_P, CTL, CTL_P )
