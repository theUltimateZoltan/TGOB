import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArbiterComponent } from './arbiter.component';

describe('ArbiterComponent', () => {
  let component: ArbiterComponent;
  let fixture: ComponentFixture<ArbiterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ArbiterComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArbiterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
